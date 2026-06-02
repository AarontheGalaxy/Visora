"""
Visualization engine.
Uses GLFW for window creation — more reliable than pygame on macOS ARM.
moderngl creates its OpenGL 3.3 Core context from the GLFW window.
Runs on the main thread (required by GLFW + OpenGL on macOS).
"""

import os
import sys
import time
import moderngl

try:
    import glfw
except ImportError:
    raise ImportError("pyglfw is required. Run: pip install pyglfw")

from audio.analyzer import AudioAnalyzer
from visualizer.modes.waveform import WaveformMode
from visualizer.modes.spectrum import SpectrumMode
from visualizer.modes.particles import ParticlesMode
from visualizer.modes.abstract import AbstractMode

SHADER_DIR = os.path.join(os.path.dirname(__file__), "shaders")

MODE_CLASSES = {
    "Waveform":  WaveformMode,
    "Spectrum":  SpectrumMode,
    "Particles": ParticlesMode,
    "Abstract":  AbstractMode,
}

TARGET_FPS = 60
FRAME_TIME = 1.0 / TARGET_FPS


class _EngineState:
    """Groups mutable render-loop state."""
    def __init__(self):
        self.running = False
        self.pending_mode = None
        self.pending_preset = None
        self.show_overlay = False
        self.extra_frame_hook = None

    def queue_mode(self, mode: str, preset: dict):
        self.pending_mode = mode
        self.pending_preset = preset

    def consume_pending(self):
        if self.pending_mode is None:
            return None
        result = (self.pending_mode, self.pending_preset or {})
        self.pending_mode = None
        self.pending_preset = None
        return result


class VisualizerEngine:
    """
    OpenGL render loop backed by GLFW.
    Audio source runs on its own thread; this class owns the GL context on the main thread.
    """

    def __init__(self, analyzer: AudioAnalyzer, initial_config: dict):
        self._analyzer = analyzer
        self._config = initial_config
        self._ctx = None
        self._mode_instance = None
        self._state = _EngineState()
        self._window = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self):
        """Blocking — must be called from the main thread."""
        if not glfw.init():
            raise RuntimeError("Failed to initialise GLFW")

        w = self._config.get("width", 1280)
        h = self._config.get("height", 720)
        fullscreen = self._config.get("fullscreen", False)

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)  # required on macOS

        monitor = glfw.get_primary_monitor() if fullscreen else None
        self._window = glfw.create_window(w, h, "Music Visualizer", monitor, None)
        if not self._window:
            glfw.terminate()
            raise RuntimeError("Failed to create GLFW window — check OpenGL 3.3 support")

        glfw.set_key_callback(self._window, self._key_callback)
        glfw.make_context_current(self._window)
        glfw.swap_interval(1)  # vsync on

        self._ctx = moderngl.create_context()
        self._ctx.enable(moderngl.PROGRAM_POINT_SIZE)

        self._load_mode(
            self._config.get("mode", "Abstract"),
            self._config.get("preset", {}),
        )

        self._state.running = True
        hook = self._state.extra_frame_hook
        last_time = time.perf_counter()

        while not glfw.window_should_close(self._window) and self._state.running:
            glfw.poll_events()

            if hook:
                hook()

            pending = self._state.consume_pending()
            if pending:
                self._load_mode(*pending)

            w_px, h_px = glfw.get_framebuffer_size(self._window)
            self._ctx.viewport = (0, 0, w_px, h_px)
            self._ctx.clear(0.0, 0.0, 0.0, 1.0)

            frame_data = self._analyzer.read_frame()
            self._mode_instance.render(frame_data, self._config.get("preset", {}))

            glfw.swap_buffers(self._window)

            now = time.perf_counter()
            sleep = FRAME_TIME - (now - last_time)
            if sleep > 0:
                time.sleep(sleep)
            last_time = time.perf_counter()

        self._cleanup()

    def set_mode(self, mode_name: str, preset: dict):
        """Queue a mode switch — safe to call from any thread."""
        self._state.queue_mode(mode_name, preset)
        self._config["mode"] = mode_name
        self._config["preset"] = preset

    def update_preset(self, preset: dict):
        self._config["preset"] = preset

    def stop(self):
        self._state.running = False

    def set_frame_hook(self, hook):
        self._state.extra_frame_hook = hook

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _key_callback(self, window, key, scancode, action, mods):
        if action != glfw.PRESS:
            return
        if key == glfw.KEY_ESCAPE:
            self._state.running = False
            glfw.set_window_should_close(window, True)
        elif key == glfw.KEY_F:
            self._state.show_overlay = not self._state.show_overlay
        elif key == glfw.KEY_TAB:
            modes = list(MODE_CLASSES.keys())
            current = self._config.get("mode", "Abstract")
            try:
                idx = modes.index(current)
            except ValueError:
                idx = 0
            nxt = (idx + 1) % len(modes)
            self.set_mode(modes[nxt], self._config.get("preset", {}))

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
        if self._window:
            glfw.destroy_window(self._window)
        glfw.terminate()
