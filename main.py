"""
Visora — Entry point.

Flow:
  1. Acquire single-instance lock (prevent duplicate windows)
  2. Show Dear PyGui selection screen (choose source, mode, preset)
  3. Start audio source thread
  4. Run OpenGL visualizer on main thread (required by macOS/GLFW)
"""

import sys

from audio.analyzer import AudioAnalyzer
from audio.sources import (
    SystemAudioSource, WindowAudioSource,
    MicrophoneSource, FileSource,
)
from presets.manager import PresetManager
from presets.favorites import FavoritesManager
from ui.selection_screen import SelectionScreen
from ui.single_instance import acquire, release
from visualizer.engine import VisualizerEngine


def main():
    """Application entry point."""
    if not acquire():
        print("Visora is already running. Close the existing window first.")
        sys.exit(1)

    try:
        _run()
    finally:
        release()


def _run():
    """Inner main — runs after the single-instance lock is held."""
    preset_manager = PresetManager()
    favorites = FavoritesManager()

    screen = SelectionScreen(preset_manager, favorites)
    config = screen.run()

    if config is None:
        sys.exit(0)

    analyzer = AudioAnalyzer()
    source = _build_source(config, analyzer)
    source.start()

    engine = VisualizerEngine(analyzer, config)
    engine.set_frame_hook(analyzer.update)

    try:
        engine.run()
    finally:
        source.stop()


def _build_source(config: dict, analyzer: AudioAnalyzer):  # noqa: PLR0911
    """Instantiate the correct audio source based on user selection."""
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
