"""
Visora — Entry point.

Flow:
  1. Acquire single-instance lock (prevent duplicate windows)
  2. Show Dear PyGui selection screen (choose source, mode, preset)
     DearPyGui uses GLFW internally; on exit it calls glfwTerminate().
  3. Start audio source thread
  4. Re-initialise GLFW and run the OpenGL visualizer on the main thread
     (safe because DearPyGui fully terminated GLFW before we get here)
"""

import sys

from audio.analyzer import AudioAnalyzer
from audio.sources import (
    FileSource, MicrophoneSource, SystemAudioSource, WindowAudioSource,
)
from presets.manager import PresetManager
from presets.favorites import FavoritesManager
from ui.selection_screen import SelectionScreen
from ui.single_instance import acquire, release
from visualizer.engine import VisualizerEngine


def main():
    if not acquire():
        print("Visora is already running. Close the existing window first.")
        sys.exit(1)

    try:
        _run()
    finally:
        release()


def _run():
    preset_manager = PresetManager()
    favorites = FavoritesManager()

    screen = SelectionScreen(preset_manager, favorites)
    config = screen.run()          # DearPyGui runs here; GLFW terminated on exit

    if config is None:
        sys.exit(0)

    analyzer = AudioAnalyzer()
    source = _build_source(config, analyzer)
    source.start()

    engine = VisualizerEngine(analyzer, config)
    engine.set_frame_hook(analyzer.update)

    try:
        engine.run()               # re-initialises GLFW, opens visualizer window
    finally:
        source.stop()


def _build_source(config: dict, analyzer: AudioAnalyzer):
    source_type = config.get("source_type", "System Audio")

    if source_type == "Microphone":
        return MicrophoneSource(analyzer)

    if source_type == "Window / App":
        return WindowAudioSource(analyzer, config.get("window_info") or {})

    if source_type == "Audio File":
        path = config.get("file_path", "")
        if not path:
            print("No audio file selected — falling back to system audio.")
            return SystemAudioSource(analyzer)
        return FileSource(analyzer, path)

    return SystemAudioSource(analyzer)


if __name__ == "__main__":
    main()
