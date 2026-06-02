"""
Visualization engine.
Uses pygame for window creation (avoids GLFW conflict with dearpygui on macOS).
moderngl creates its OpenGL context from the active pygame GL surface.
Runs on the main thread (required by pygame + OpenGL on macOS).
"""

import os
import pygame
import moderngl

from audio.analyzer import AudioAnalyzer
from visualizer.modes.waveform import WaveformMode
from visualizer.modes.spectrum import SpectrumMode
from visualizer.modes.particles import ParticlesMode
from visualizer.modes.abstract import AbstractMode

SHADER_DIR = os.path.join(os.path.dirname(__file__), "shaders")

MODE_CLASSES = {
    "Waveform": WaveformMode,
    "Spectrum": SpectrumMode,
    "Particles": ParticlesMode,
    "Abstract": AbstractMode,
}

TARGET_FPS = 60
FRAME_TIME = 1.0 / TARGET_FPS


class _EngineState:
    """Groups mutable render-loop state to stay under the attribute limit."""
    def __init__(self):
        self.running = False
        self.pending_mode: str | None = None
        self.pending_preset: dict | None = None
        self.show_overlay = False
        self.extra_frame_hook = None

    def queue_mode(self, mode: str, preset: dict):
        """Queue a mode switch to be applied on the next frame."""
        self.pending_mode = mode
        self.pending_preset = preset

    def consume_pending(self) -> tuple[str, dict] | None:
        """Return and clear any queued mode switch, or None if none pending."""
        if self.pending_mode is None:
            return None
        result = (self.pending_mode, self.pending_preset or {})
        self.pending_mode = None
        self.pending_preset = None
        return result


class VisualizerEngine:
    """
    OpenGL render loop backed by pygame.
    Audio source runs on its own thread; this class owns the GL context on the main thread.
    Mode/preset switches are queued from any thread via set_mode() and applied each frame.
    """

    def __init__(self, analyzer: AudioAnalyzer, initial_config: dict):
        self._analyzer = analyzer
        self._config = initial_config
        self._ctx: moderngl.Context | None = None
        self._mode_instance = None
        self._state = _EngineState()
        self._clock = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self):
        """Blocking — must be called from the main thread."""
        pygame.init()
        pygame.display.set_caption("Music Visualizer")

        w = self._config.get("width", 1280)
        h = self._config.get("height", 720)
        fullscreen = self._config.get("fullscreen", False)

        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_PROFILE_MASK,
            pygame.GL_CONTEXT_PROFILE_CORE,
        )
        # MSAA removed: GL_MULTISAMPLEBUFFERS + GL_MULTISAMPLESAMPLES cause
        # SIGBUS on macOS ARM (Apple Silicon) with the legacy OpenGL stack.

        flags = pygame.OPENGL | pygame.DOUBLEBUF
        if fullscreen:
            flags |= pygame.FULLSCREEN

        pygame.display.set_mode((w, h), flags)

        self._ctx = moderngl.create_context()
        self._ctx.enable(moderngl.PROGRAM_POINT_SIZE)

        self._load_mode(
            self._config.get("mode", "Abstract"),
            self._config.get("preset", {}),
        )

        self._clock = pygame.time.Clock()
        self._state.running = True
        hook = self._state.extra_frame_hook

        while self._state.running:
            # --- Events ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._state.running = False
                elif event.type == pygame.KEYDOWN:
                    self._handle_key(event.key)
                elif event.type == pygame.VIDEORESIZE:
                    self._ctx.viewport = (0, 0, event.w, event.h)

            # --- Audio update (FFT + beat detection) ---
            if hook:
                hook()

            # --- Apply queued mode/preset switch ---
            pending = self._state.consume_pending()
            if pending:
                self._load_mode(*pending)

            # --- Render ---
            w_px, h_px = pygame.display.get_surface().get_size()
            self._ctx.viewport = (0, 0, w_px, h_px)
            self._ctx.clear(0.0, 0.0, 0.0, 1.0)

            frame_data = self._analyzer.read_frame()
            self._mode_instance.render(frame_data, self._config.get("preset", {}))

            pygame.display.flip()
            self._clock.tick(TARGET_FPS)

        self._cleanup()

    def set_mode(self, mode_name: str, preset: dict):
        """Queue a mode switch — safe to call from any thread."""
        self._state.queue_mode(mode_name, preset)
        self._config["mode"] = mode_name
        self._config["preset"] = preset

    def update_preset(self, preset: dict):
        """Update active preset params — safe to call from any thread."""
        self._config["preset"] = preset

    def stop(self):
        """Request render loop to stop."""
        self._state.running = False

    def set_frame_hook(self, hook):
        """Register a callable invoked once per render frame before drawing."""
        self._state.extra_frame_hook = hook

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _load_mode(self, mode_name: str, preset: dict):
        if self._mode_instance is not None:
            self._mode_instance.cleanup()
        cls = MODE_CLASSES.get(mode_name, AbstractMode)
        self._mode_instance = cls(self._ctx, SHADER_DIR)
        self._config["mode"] = mode_name
        self._config["preset"] = preset

    def _cleanup(self):
        if self._mode_instance:
            self._mode_instance.cleanup()
        pygame.quit()

    def _handle_key(self, key: int):
        if key == pygame.K_ESCAPE:
            self._state.running = False
        elif key == pygame.K_f:
            self._state.show_overlay = not self._state.show_overlay
        elif key == pygame.K_TAB:
            modes = list(MODE_CLASSES.keys())
            current = self._config.get("mode", "Abstract")
            try:
                idx = modes.index(current)
            except ValueError:
                idx = 0
            nxt = (idx + 1) % len(modes)
            self.set_mode(modes[nxt], self._config.get("preset", {}))
