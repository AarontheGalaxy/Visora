"""
All in-app help text. Centralised so it's easy to update.
Each entry: title + body (markdown-style, rendered as plain text in Dear PyGui).
"""

SECTIONS = {
    "welcome": {
        "title": "Welcome to Music Visualizer",
        "body": (
            "Music Visualizer turns any sound on your computer into a live, "
            "colourful animation.\n\n"
            "This guide explains every feature. You can return here any time "
            "by clicking the  ?  button in the top-right corner.\n\n"
            "Quick start:\n"
            "  1. Choose an Audio Source (what sound to listen to)\n"
            "  2. Choose a Visualization Mode (what the animation looks like)\n"
            "  3. Pick a Preset or colour palette\n"
            "  4. Click  Launch \n\n"
            "Once the visualizer is open:\n"
            "  TAB  = cycle through modes\n"
            "  ESC  = close the visualizer\n"
            "  F    = toggle info overlay (FPS etc.)"
        ),
    },

    "audio_source": {
        "title": "Audio Source",
        "body": (
            "This controls WHAT sound the visualizer listens to.\n\n"

            "System Audio\n"
            "  Captures everything playing on your computer — music, videos,\n"
            "  games, browser tabs. The most common choice.\n"
            "  On macOS you may see a permission prompt the first time.\n\n"

            "Microphone\n"
            "  Listens to your microphone. Good for singing, clapping or\n"
            "  instruments in the room. The visualizer reacts to your voice.\n\n"

            "Window / App\n"
            "  Picks the audio from ONE specific application (e.g. Spotify,\n"
            "  Chrome, VLC). Click 'Refresh app list' to see running apps,\n"
            "  then click the app you want.\n"
            "  Note: on macOS this requires Screen Recording permission.\n\n"

            "Audio File\n"
            "  Load an MP3, WAV, FLAC or OGG file from your computer.\n"
            "  The visualizer plays and reacts to that file.\n"
            "  Click 'Browse…' to pick a file."
        ),
    },

    "vis_mode": {
        "title": "Visualization Mode",
        "body": (
            "The mode decides the STYLE of the animation.\n\n"

            "Abstract  (recommended)\n"
            "  A full-screen plasma / fractal shader inspired by Milkdrop.\n"
            "  Bass makes the image pulse, highs add shimmer.\n"
            "  Most visually impressive. Good for music or ambient sound.\n\n"

            "Spectrum\n"
            "  Classic frequency bars — like Winamp / iTunes visualizer.\n"
            "  Left = bass (low frequencies), right = treble (highs).\n"
            "  The taller a bar, the louder that frequency is right now.\n\n"

            "Waveform\n"
            "  An oscilloscope — shows the raw audio wave as a line.\n"
            "  Good for seeing the shape of instruments and vocals.\n\n"

            "Particles\n"
            "  Sparks shoot out on every beat. More bass = bigger burst.\n"
            "  Great for energetic music like EDM or hip-hop.\n\n"

            "Tip: press TAB while the visualizer is running to cycle modes live."
        ),
    },

    "presets": {
        "title": "Presets",
        "body": (
            "A preset is a saved combination of settings for a mode.\n"
            "Think of it like a 'theme' or 'style' for the visualizer.\n\n"

            "Built-in\n"
            "  Presets that come with the app. You cannot delete these.\n"
            "  Examples: 'Neon Plasma', 'Fire Spectrum', 'Galaxy Particles'.\n\n"

            "My Presets\n"
            "  Presets you have saved yourself. You can delete these.\n"
            "  To create one: tweak the settings in the visualizer, then\n"
            "  open the in-app menu (press M) and click 'Save as preset'.\n\n"

            "Favorites ★\n"
            "  Presets you have marked as favorites for quick access.\n"
            "  Click any preset, then press the  ★ Favorite  button.\n\n"

            "Importing a .milk file\n"
            "  .milk files are Milkdrop presets — thousands are freely\n"
            "  available online (e.g. https://github.com/projectM-visualizer).\n"
            "  Click 'Import .milk', pick the file, and it appears in\n"
            "  'My Presets'. These run in Abstract mode.\n\n"

            "Selecting a preset applies its colours, speed and style\n"
            "to the chosen Visualization Mode."
        ),
    },

    "favorites": {
        "title": "Favorites ★",
        "body": (
            "Favorites let you bookmark the presets you love most so you\n"
            "can find them instantly.\n\n"
            "How to add a favorite:\n"
            "  1. Click a preset in the Built-in or My Presets list\n"
            "  2. Click the  ★ Favorite  button below the list\n"
            "  3. The preset moves into the Favorites tab\n\n"
            "How to remove a favorite:\n"
            "  1. Click the preset in the Favorites tab\n"
            "  2. Click the  ★ Unfav  button\n\n"
            "Your favorites are saved automatically and remembered\n"
            "every time you open the app."
        ),
    },

    "color_palette": {
        "title": "Color Palette",
        "body": (
            "The palette controls the main colours of the visualizer.\n\n"
            "Neon    — electric purple + teal. Vivid and cyberpunk.\n"
            "Fire    — deep red to bright yellow. Hot and energetic.\n"
            "Ice     — cool blue-white. Calm and clean.\n"
            "Sunset  — orange and warm gold. Relaxed and warm.\n"
            "Purple  — violet tones. Great for lo-fi or ambient.\n"
            "Mono    — pure white. Minimal, works with any mode.\n\n"
            "The palette blends with the preset's own colours,\n"
            "so results vary per mode."
        ),
    },

    "milk_import": {
        "title": "Importing .milk Presets",
        "body": (
            "Milkdrop (.milk) presets are visual programs made for the\n"
            "Winamp Milkdrop plugin and compatible with projectM.\n"
            "Thousands of free presets exist online.\n\n"
            "Where to find .milk files:\n"
            "  • Search GitHub for 'milkdrop presets'\n"
            "  • https://github.com/projectM-visualizer/presets-milkdrop-\n"
            "    converted (official projectM preset collection)\n"
            "  • SourceForge, Winamp forums\n\n"
            "How to import:\n"
            "  1. Download a .milk file to your computer\n"
            "  2. In the setup screen, click  Import .milk \n"
            "  3. Browse to the file and select it\n"
            "  4. It appears in 'My Presets' immediately\n"
            "  5. Select it and click  Launch \n\n"
            "Note: complex .milk shader code is partially supported.\n"
            "Simple parameter presets (colours, zoom, rotation) import\n"
            "fully. Custom HLSL shaders are mapped to Abstract mode."
        ),
    },

    "window_size": {
        "title": "Window Size",
        "body": (
            "Sets the size of the visualizer window.\n\n"
            "1280 × 720   — Standard HD. Works on any display.\n"
            "1920 × 1080  — Full HD. Sharp on large screens.\n"
            "2560 × 1440  — 2K. Requires a capable GPU.\n"
            "Fullscreen   — Takes over the entire screen.\n"
            "               Press ESC to exit fullscreen.\n\n"
            "Tip: larger sizes are more demanding on your GPU.\n"
            "If the animation stutters, try a smaller size."
        ),
    },

    "keyboard_shortcuts": {
        "title": "Keyboard Shortcuts (Visualizer)",
        "body": (
            "While the visualizer is running:\n\n"
            "  TAB      Cycle to the next visualization mode\n"
            "  ESC      Close the visualizer\n"
            "  F        Toggle FPS / debug overlay\n\n"
            "Coming soon:\n"
            "  M        Open in-app settings menu\n"
            "  S        Save current state as a preset\n"
            "  SPACE    Pause / resume audio reaction"
        ),
    },

    "performance": {
        "title": "Performance Tips",
        "body": (
            "If the visualizer is slow or choppy:\n\n"
            "  • Use a smaller window size (1280×720 is fastest)\n"
            "  • Switch from Abstract or Particles to Waveform or Spectrum\n"
            "    (shader modes are more GPU-intensive)\n"
            "  • Close other apps that use the GPU (games, browsers)\n"
            "  • On laptops, plug in the charger — battery saving\n"
            "    mode throttles the GPU\n\n"
            "The app targets 60 frames per second. The FPS overlay\n"
            "(press F) shows the actual frame rate."
        ),
    },
}

# Short tooltip text shown on hover (one line each)
TOOLTIPS = {
    "source_type":         "Where to listen for audio — your whole computer, a microphone, one specific app, or a file.",
    "window_list":         "Apps currently running on your computer. Click one to capture only its audio.",
    "file_path":           "Path to the audio file you want to visualize. Supports MP3, WAV, FLAC, OGG.",
    "vis_mode":            "The visual style of the animation. Try Abstract for the most impressive result.",
    "builtin_preset_list": "Ready-made styles that come with the app.",
    "user_preset_list":    "Styles you have saved yourself. Create them from inside the visualizer.",
    "fav_preset_list":     "Your bookmarked presets for quick access.",
    "fav_btn":             "Add or remove the selected preset from your Favorites list.",
    "palette":             "The main colour scheme. Blends with the preset's own colours.",
    "window_size":         "Size of the visualizer window. Larger = sharper but needs more GPU power.",
    "launch_btn":          "Start the visualizer with the settings you have chosen.",
}
