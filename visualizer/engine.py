"""
Visualization engine.
Uses pyglet for window creation — does not conflict with DearPyGui's
bundled GLFW (they each use separate Objective-C class namespaces on macOS).
moderngl creates its OpenGL 3.3 Core context from the active pyglet window.
Runs on the main thread (required on macOS).
"""

import os
import moderngl

try:
    import pyglet
    import pyglet.gl
    from pyglet.window import key as pyglet_key
except ImportError:
    raise ImportError("pyglet is required. Run: pip install pyglet")

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


class _EngineState:
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
    OpenGL render loop backed by pyglet.
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

    def run(self):
        """Blocking — must be called from the main thread."""
        w = self._config.get("width", 1280)
        h = self._config.get("height", 720)
        fullscreen = self._config.get("fullscreen", False)

        gl_config = pyglet.gl.Config(
            major_version=3,
            minor_version=3,
            forward_compat=True,
            core_profile=True,
            double_buffer=True,
            depth_size=24,
        )

        self._window = pyglet.window.Window(
            width=w,
            height=h,
            caption="Music Visualizer",
            fullscreen=fullscreen,
            config=gl_config,
            resizable=False,
            vsync=True,
        )

        self._ctx = moderngl.create_context(require=330)
        self._ctx.enable(moderngl.PROGRAM_POINT_SIZE)

        self._load_mode(
            self._config.get("mode", "Abstract"),
            self._config.get("preset", {}),
        )

        self._state.running = True
        hook = self._state.extra_frame_hook

        engine = self

        @self._window.event
        def on_draw():
            if not engine._state.running:
                return

            if hook:
                hook()

            pending = engine._state.consume_pending()
            if pending:
                engine._load_mode(*pending)

            try:
                fb_w, fb_h = engine._window.get_framebuffer_size()
            except AttributeError:
                fb_w, fb_h = engine._window.width, engine._window.height

            engine._ctx.viewport = (0, 0, fb_w, fb_h)
            engine._ctx.clear(0.0, 0.0, 0.0, 1.0)

            frame_data = engine._analyzer.read_frame()
            engine._mode_instance.render(frame_data, engine._config.get("preset", {}))

        @self._window.event
        def on_key_press(symbol, modifiers):
            if symbol == pyglet_key.ESCAPE:
                engine._state.running = False
                engine._window.close()
            elif symbol == pyglet_key.F:
                engine._state.show_overlay = not engine._state.show_overlay
            elif symbol == pyglet_key.TAB:
                modes = list(MODE_CLASSES.keys())
                current = engine._config.get("mode", "Abstract")
                try:
                    idx = modes.index(current)
                except ValueError:
                    idx = 0
                nxt = (idx + 1) % len(modes)
                engine.set_mode(modes[nxt], engine._config.get("preset", {}))

        @self._window.event
        def on_close():
            engine._state.running = False

        pyglet.clock.schedule_interval(lambda dt: engine._window.dispatch_event("on_draw"), 1 / TARGET_FPS)
        pyglet.app.run()

        self._cleanup()

    def set_mode(self, mode_name: str, preset: dict):
        self._state.queue_mode(mode_name, preset)
        self._config["mode"] = mode_name
        self._config["preset"] = preset

    def update_preset(self, preset: dict):
        self._config["preset"] = preset

    def stop(self):
        self._state.running = False

    def set_frame_hook(self, hook):
        self._state.extra_frame_hook = hook

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
