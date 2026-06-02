"""
Visora — Entry point.

Flow:
  1. Acquire single-instance lock (prevent duplicate windows)
  2. Show Dear PyGui selection screen (choose source, mode, preset)
  3. Launch visualizer in a subprocess (isolates DearPyGui SDL2 from pygame SDL2)
"""

import json
import os
import subprocess
import sys

from presets.manager import PresetManager
from presets.favorites import FavoritesManager
from ui.selection_screen import SelectionScreen
from ui.single_instance import acquire, release


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

    # Launch the visualizer in a fresh subprocess so that DearPyGui's bundled
    # SDL2 and pygame's SDL2 never coexist in the same process (they conflict
    # on macOS, causing a segfault during OpenGL context creation).
    config_json = json.dumps(config)
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_run_visualizer.py")
    subprocess.run(
        [sys.executable, script],
        input=config_json.encode(),
    )


if __name__ == "__main__":
    main()
