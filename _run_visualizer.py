"""
Subprocess worker for the visualizer.
Launched by main.py to isolate DearPyGui's SDL2 from pygame's SDL2 on macOS.
Reads the config dict as JSON from stdin.
"""

import json
import sys


def _build_source(config: dict, analyzer):
    from audio.sources import (
        FileSource, MicrophoneSource, SystemAudioSource, WindowAudioSource,
    )
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


def main():
    try:
        config = json.loads(sys.stdin.read())
    except Exception as exc:
        print(f"Visualizer: failed to read config: {exc}")
        sys.exit(1)

    from audio.analyzer import AudioAnalyzer
    from visualizer.engine import VisualizerEngine

    analyzer = AudioAnalyzer()
    source = _build_source(config, analyzer)
    source.start()

    engine = VisualizerEngine(analyzer, config)
    engine.set_frame_hook(analyzer.update)

    try:
        engine.run()
    finally:
        source.stop()


if __name__ == "__main__":
    main()
