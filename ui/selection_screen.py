"""
Launch selection screen — Dear PyGui.
Features:
  - Audio source selection (system, mic, window/app with search, file)
  - Visualization mode picker
  - Preset browser (built-in / user / favorites) with import .milk
  - Color palette picker
  - Window size selector
  - Tooltips on every control
  - Full in-app help window with per-feature guides
"""

import threading
import dearpygui.dearpygui as dpg


from audio.sources import list_audio_windows
from presets.manager import PresetManager
from presets.favorites import FavoritesManager
from ui.help_content import SECTIONS

MODES = ["Abstract", "Spectrum", "Waveform", "Particles"]
SOURCE_TYPES = ["System Audio", "Microphone", "Window / App", "Audio File"]
PALETTES = {
    "Neon":   {"color_a": [0.05, 0.0, 0.4],  "color_b": [0.0, 1.0, 0.7]},
    "Fire":   {"color_low": [0.8, 0.1, 0.0], "color_high": [1.0, 0.9, 0.1]},
    "Ice":    {"color": [0.4, 0.8, 1.0]},
    "Sunset": {"color_a": [0.5, 0.05, 0.0],  "color_b": [1.0, 0.6, 0.0]},
    "Purple": {"color": [0.6, 0.2, 1.0]},
    "Mono":   {"color": [1.0, 1.0, 1.0]},
}


class SelectionScreen:
    """
    Dear PyGui launch screen.
    Blocks on run() until the user clicks Launch or closes the window,
    then returns a config dict (or None if cancelled).
    """

    def __init__(self, preset_manager: PresetManager, favorites: FavoritesManager):
        self._presets = preset_manager
        self._favorites = favorites
        self._result: dict | None = None
        self._all_windows: list[dict] = []
        self._filtered_windows: list[dict] = []
        self._done = threading.Event()

    # ------------------------------------------------------------------
    def run(self) -> dict | None:
        """Show the setup screen and block until the user launches or quits."""
        self._init_dpg()
        self._run_loop()
        dpg.destroy_context()
        return self._result

    def open_help(self, topic: str = "welcome"):
        """Programmatically open the help panel on a given topic."""
        self._show_help(topic)

    # ------------------------------------------------------------------

    def _init_dpg(self):
        dpg.create_context()
        dpg.create_viewport(
            title="Music Visualizer — Setup",
            width=960, height=700,
            resizable=False,
        )
        dpg.setup_dearpygui()
        self._apply_theme()
        self._build_ui()
        self._build_help_window()
        dpg.show_viewport()

    def _run_loop(self):
        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
            if self._done.is_set():
                break

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def _apply_theme(self):
        with dpg.theme() as t:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg,        (16, 16, 26))
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg,         (22, 22, 36))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg,         (32, 32, 52))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered,  (48, 48, 76))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive,   (58, 48, 96))
                dpg.add_theme_color(dpg.mvThemeCol_Button,          (55, 35, 110))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,   (85, 55, 170))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,    (105, 75, 210))
                dpg.add_theme_color(dpg.mvThemeCol_Header,          (55, 35, 110))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered,   (75, 50, 150))
                dpg.add_theme_color(dpg.mvThemeCol_SliderGrab,      (120, 80, 230))
                dpg.add_theme_color(dpg.mvThemeCol_CheckMark,       (120, 80, 230))
                dpg.add_theme_color(dpg.mvThemeCol_Tab,             (40, 30, 80))
                dpg.add_theme_color(dpg.mvThemeCol_TabHovered,      (70, 50, 140))
                dpg.add_theme_color(dpg.mvThemeCol_TabActive,       (90, 65, 180))
                dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive,   (40, 25, 90))
                dpg.add_theme_color(dpg.mvThemeCol_Separator,       (60, 50, 100))
                dpg.add_theme_color(dpg.mvThemeCol_Text,            (218, 218, 240))
                dpg.add_theme_color(dpg.mvThemeCol_TextDisabled,    (110, 110, 140))
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg,     (18, 18, 28))
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab,   (70, 50, 140))
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding,   8)
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding,  12)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding,   8)
                dpg.add_theme_style(dpg.mvStyleVar_PopupRounding,   8)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing,     10, 8)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding,    10, 6)
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding,   16, 14)
        dpg.bind_theme(t)

    # ------------------------------------------------------------------
    # Main UI
    # ------------------------------------------------------------------

    def _build_ui(self):
        with dpg.window(tag="main_window", no_title_bar=True, no_resize=True,
                        no_move=True, width=960, height=700, pos=(0, 0)):

            # ── Header ──────────────────────────────────────────────
            with dpg.group(horizontal=True):
                dpg.add_text("Music Visualizer", color=(170, 130, 255))
                dpg.add_spacer(width=16)
                dpg.add_button(
                    label=" ? Help & Guide ",
                    callback=lambda: dpg.show_item("help_window"),
                    tag="open_help_btn",
                )
            dpg.add_text(
                "Pick your settings below, then click Launch. "
                "Hover over any control for a quick tip.",
                color=(150, 150, 180),
            )
            dpg.add_spacer(height=6)
            dpg.add_separator()
            dpg.add_spacer(height=8)

            # ── Two columns ─────────────────────────────────────────
            with dpg.group(horizontal=True):
                self._build_left_column()
                dpg.add_spacer(width=10)
                self._build_right_column()

            # ── Launch / Quit ────────────────────────────────────────
            dpg.add_spacer(height=10)
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="   Launch   ",
                    tag="launch_btn",
                    callback=self._on_launch,
                    width=220, height=46,
                )
                dpg.add_spacer(width=8)
                dpg.add_button(
                    label="   Quit   ",
                    callback=lambda: dpg.stop_dearpygui(),
                    width=110, height=46,
                )


        # ── File dialogs ─────────────────────────────────────────────
        with dpg.file_dialog(
            tag="file_dialog", show=False, width=640, height=440,
            callback=self._on_file_selected,
        ):
            dpg.add_file_extension(".mp3")
            dpg.add_file_extension(".wav")
            dpg.add_file_extension(".flac")
            dpg.add_file_extension(".ogg")

        with dpg.file_dialog(
            tag="milk_dialog", show=False, width=640, height=440,
            callback=self._on_milk_selected,
        ):
            dpg.add_file_extension(".milk")

    # ------------------------------------------------------------------
    # Left column — audio source + mode
    # ------------------------------------------------------------------

    def _build_left_column(self):
        with dpg.child_window(width=430, height=560, border=True):

            # ── Audio Source ─────────────────────────────────────────
            with dpg.group(horizontal=True):
                dpg.add_text("Audio Source", color=(180, 140, 255))
                dpg.add_spacer(width=6)
                dpg.add_button(
                    label="?", width=22, height=22,
                    callback=lambda: self._show_help("audio_source"),
                )
            dpg.add_spacer(height=4)

            dpg.add_radio_button(
                items=SOURCE_TYPES,
                tag="source_type",
                default_value="System Audio",
                callback=self._on_source_type_change,
            )

            dpg.add_spacer(height=8)

            # Window / App picker ─────────────────────────────────────
            with dpg.group(tag="window_picker_group", show=False):
                with dpg.group(horizontal=True):
                    dpg.add_text("Application:", color=(160, 160, 200))
                    dpg.add_spacer(width=6)
                    dpg.add_button(
                        label="?", width=22, height=22,
                        callback=lambda: self._show_help("audio_source"),
                    )

                # Search box
                dpg.add_input_text(
                    tag="window_search",
                    hint="Search app name…",
                    width=-1,
                    callback=self._on_window_search,
                )
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Refresh list",
                        callback=self._refresh_windows,
                        width=130,
                    )
                    dpg.add_text("", tag="window_count_label", color=(140, 140, 170))

                dpg.add_listbox(
                    items=[],
                    tag="window_list",
                    num_items=7,
                    width=-1,
                )
                dpg.add_spacer(height=6)

            # File picker ─────────────────────────────────────────────
            with dpg.group(tag="file_picker_group", show=False):
                dpg.add_text("Audio file:", color=(160, 160, 200))
                dpg.add_input_text(tag="file_path", hint="Path to MP3/WAV…", width=-1)
                dpg.add_button(
                    label="Browse…",
                    callback=lambda: dpg.show_item("file_dialog"),
                    width=-1,
                )
                dpg.add_spacer(height=6)

            dpg.add_separator()
            dpg.add_spacer(height=8)

            # ── Visualization Mode ────────────────────────────────────
            with dpg.group(horizontal=True):
                dpg.add_text("Visualization Mode", color=(180, 140, 255))
                dpg.add_spacer(width=6)
                dpg.add_button(
                    label="?", width=22, height=22,
                    callback=lambda: self._show_help("vis_mode"),
                )
            dpg.add_spacer(height=4)

            dpg.add_radio_button(
                items=MODES,
                tag="vis_mode",
                default_value="Abstract",
                callback=self._on_mode_change,
            )

            dpg.add_spacer(height=8)

            # Mode description ────────────────────────────────────────
            dpg.add_text(
                "Abstract: Milkdrop-style plasma shader. Most visual.",
                tag="mode_desc",
                color=(140, 140, 175),
                wrap=400,
            )

    # ------------------------------------------------------------------
    # Right column — presets + palette + size
    # ------------------------------------------------------------------

    def _build_right_column(self):
        with dpg.child_window(width=490, height=560, border=True):

            # ── Presets ───────────────────────────────────────────────
            with dpg.group(horizontal=True):
                dpg.add_text("Presets", color=(180, 140, 255))
                dpg.add_spacer(width=6)
                dpg.add_button(
                    label="?", width=22, height=22,
                    callback=lambda: self._show_help("presets"),
                )

            dpg.add_spacer(height=4)

            with dpg.tab_bar(tag="preset_tabs"):
                with dpg.tab(label="Built-in"):
                    dpg.add_listbox(
                        items=self._preset_names(builtin=True),
                        tag="builtin_preset_list",
                        num_items=7,
                        width=-1,
                        callback=self._on_preset_select,
                    )

                with dpg.tab(label="My Presets"):
                    dpg.add_listbox(
                        items=self._preset_names(builtin=False),
                        tag="user_preset_list",
                        num_items=7,
                        width=-1,
                        callback=self._on_preset_select,
                    )

                with dpg.tab(label="Favorites ★"):
                    dpg.add_listbox(
                        items=self._favorites.names,
                        tag="fav_preset_list",
                        num_items=7,
                        width=-1,
                        callback=self._on_preset_select,
                    )

            dpg.add_spacer(height=6)

            # Preset action buttons ───────────────────────────────────
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="★  Favorite",
                    tag="fav_btn",
                    callback=self._toggle_favorite,
                    width=140,
                )

                dpg.add_spacer(width=6)

                dpg.add_button(
                    label="Import .milk",
                    tag="import_milk_btn",
                    callback=lambda: dpg.show_item("milk_dialog"),
                    width=140,
                )

                dpg.add_spacer(width=6)

                dpg.add_button(
                    label="?  .milk guide",
                    callback=lambda: self._show_help("milk_import"),
                    width=140,
                )

            dpg.add_separator()
            dpg.add_spacer(height=8)

            # ── Color Palette ─────────────────────────────────────────
            with dpg.group(horizontal=True):
                dpg.add_text("Color Palette", color=(180, 140, 255))
                dpg.add_spacer(width=6)
                dpg.add_button(
                    label="?", width=22, height=22,
                    callback=lambda: self._show_help("color_palette"),
                )
            dpg.add_spacer(height=4)

            dpg.add_combo(
                items=list(PALETTES.keys()),
                tag="palette",
                default_value="Neon",
                width=-1,
            )
            dpg.add_separator()
            dpg.add_spacer(height=8)

            # ── Window Size ───────────────────────────────────────────
            with dpg.group(horizontal=True):
                dpg.add_text("Window Size", color=(180, 140, 255))
                dpg.add_spacer(width=6)
                dpg.add_button(
                    label="?", width=22, height=22,
                    callback=lambda: self._show_help("window_size"),
                )
            dpg.add_spacer(height=4)

            dpg.add_combo(
                items=["1280 × 720", "1920 × 1080", "2560 × 1440", "Fullscreen"],
                tag="window_size",
                default_value="1280 × 720",
                width=-1,
            )
            dpg.add_separator()
            dpg.add_spacer(height=8)

            # ── Keyboard Shortcuts quick reference ────────────────────
            with dpg.group(horizontal=True):
                dpg.add_text("Keyboard Shortcuts", color=(140, 140, 175))
                dpg.add_spacer(width=6)
                dpg.add_button(
                    label="?", width=22, height=22,
                    callback=lambda: self._show_help("keyboard_shortcuts"),
                )
            dpg.add_text(
                "TAB = cycle modes    ESC = close    F = FPS overlay",
                color=(110, 110, 145),
                wrap=460,
            )

    # ------------------------------------------------------------------
    # Help window
    # ------------------------------------------------------------------

    def _build_help_window(self):
        with dpg.window(
            label="Help & Guide",
            tag="help_window",
            show=False,
            width=680, height=520,
            pos=(140, 90),
            on_close=lambda: dpg.hide_item("help_window"),
        ):
            with dpg.group(horizontal=True):
                # Left: topic list
                with dpg.child_window(width=200, height=460, border=True):
                    dpg.add_text("Topics", color=(180, 140, 255))
                    dpg.add_spacer(height=6)
                    topic_labels = {
                        "welcome":            "Getting Started",
                        "audio_source":       "Audio Source",
                        "vis_mode":           "Visualization Mode",
                        "presets":            "Presets",
                        "favorites":          "Favorites ★",
                        "color_palette":      "Color Palette",
                        "milk_import":        "Importing .milk",
                        "window_size":        "Window Size",
                        "keyboard_shortcuts": "Keyboard Shortcuts",
                        "performance":        "Performance Tips",
                    }
                    for topic_key, topic_label in topic_labels.items():
                        dpg.add_button(
                            label=topic_label,
                            width=-1,
                            callback=self._make_topic_cb(topic_key),
                        )
                        dpg.add_spacer(height=2)

                dpg.add_spacer(width=10)

                # Right: content
                with dpg.child_window(width=450, height=460, border=True, tag="help_content_panel"):
                    dpg.add_text(
                        SECTIONS["welcome"]["title"],
                        tag="help_title",
                        color=(200, 170, 255),
                    )
                    dpg.add_separator()
                    dpg.add_spacer(height=4)
                    dpg.add_text(
                        SECTIONS["welcome"]["body"],
                        tag="help_body",
                        wrap=420,
                        color=(210, 210, 230),
                    )

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _on_source_type_change(self, _, value):
        dpg.configure_item("window_picker_group", show=value == "Window / App")
        dpg.configure_item("file_picker_group",   show=value == "Audio File")
        if value == "Window / App":
            self._refresh_windows()

    def _on_mode_change(self, _, value):
        descs = {
            "Abstract":  "Abstract: Milkdrop-style plasma shader. Most visual.",
            "Spectrum":  "Spectrum: Classic frequency bars — left=bass, right=treble.",
            "Waveform":  "Waveform: Raw oscilloscope line. Shows audio shape.",
            "Particles": "Particles: Sparks burst on every beat. Great for EDM.",
        }
        dpg.set_value("mode_desc", descs.get(value, ""))
        names = self._preset_names(builtin=True, mode=value)
        dpg.configure_item("builtin_preset_list", items=names)

    def _on_preset_select(self, _, value):
        if not value:
            return
        preset = self._presets.get(value)
        if preset:
            dpg.set_value("vis_mode", preset.mode)
            self._on_mode_change(None, preset.mode)
        is_fav = self._favorites.is_favorite(value)
        dpg.configure_item("fav_btn", label="★  Unfav" if is_fav else "★  Favorite")

    def _toggle_favorite(self):
        name = self._selected_preset_name()
        if not name:
            return
        preset = self._presets.get(name)
        if not preset:
            return
        now_fav = self._favorites.toggle(name, preset.mode)
        dpg.configure_item("fav_btn", label="★  Unfav" if now_fav else "★  Favorite")
        dpg.configure_item("fav_preset_list", items=self._favorites.names)

    def _on_file_selected(self, _, app_data):
        path = app_data.get("file_path_name", "")
        dpg.set_value("file_path", path)

    def _on_milk_selected(self, _, app_data):
        path = app_data.get("file_path_name", "")
        if path:
            preset = self._presets.import_milk(path)
            dpg.configure_item(
                "user_preset_list",
                items=self._preset_names(builtin=False),
            )
            dpg.set_value("user_preset_list", preset.name)

    def _refresh_windows(self):
        self._all_windows = list_audio_windows()
        self._filtered_windows = list(self._all_windows)
        self._update_window_list_ui()

    def _on_window_search(self, _, value: str):
        q = value.strip().lower()
        self._filtered_windows = (
            [w for w in self._all_windows if q in w["name"].lower()]
            if q else list(self._all_windows)
        )
        self._update_window_list_ui()

    def _update_window_list_ui(self):
        labels = [f"{w['name']}  (pid {w['pid']})" for w in self._filtered_windows]
        dpg.configure_item("window_list", items=labels)
        count = len(self._filtered_windows)
        total = len(self._all_windows)
        dpg.set_value(
            "window_count_label",
            f"  {count}/{total} apps" if count != total else f"  {total} apps",
        )

    def _on_launch(self):
        mode        = dpg.get_value("vis_mode")
        source_type = dpg.get_value("source_type")
        palette     = PALETTES.get(dpg.get_value("palette"), {})
        preset_name = self._selected_preset_name()
        preset      = self._presets.get(preset_name) if preset_name else None
        params      = {**(preset.params if preset else {}), **palette}
        width, height, fullscreen = self._parse_size(dpg.get_value("window_size"))

        self._result = {
            "mode":        mode,
            "preset":      params,
            "source_type": source_type,
            "window_info": self._resolve_window_info(source_type),
            "file_path":   dpg.get_value("file_path") if source_type == "Audio File" else None,
            "width":       width,
            "height":      height,
            "fullscreen":  fullscreen,
        }
        self._done.set()
        dpg.stop_dearpygui()

    def _resolve_window_info(self, source_type: str) -> dict | None:
        if source_type != "Window / App":
            return None
        sel_label = dpg.get_value("window_list")
        return next(
            (w for w in self._filtered_windows
             if f"{w['name']}  (pid {w['pid']})" == sel_label),
            None,
        )

    # ------------------------------------------------------------------
    # Help helpers
    # ------------------------------------------------------------------

    def _show_help(self, key: str):
        section = SECTIONS.get(key, SECTIONS["welcome"])
        dpg.set_value("help_title", section["title"])
        dpg.set_value("help_body", section["body"])
        dpg.show_item("help_window")

    def _make_topic_cb(self, key: str):
        def cb():
            self._show_help(key)
        return cb

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _preset_names(self, builtin: bool, mode: str | None = None) -> list[str]:
        lst = self._presets.builtin_presets if builtin else self._presets.user_presets
        if mode:
            lst = [p for p in lst if p.mode == mode]
        return [p.name for p in lst]

    def _selected_preset_name(self) -> str | None:
        for tag in ("builtin_preset_list", "user_preset_list", "fav_preset_list"):
            val = dpg.get_value(tag)
            if val:
                return val
        return None

    @staticmethod
    def _parse_size(s: str) -> tuple[int, int, bool]:
        mapping = {
            "1280 × 720":  (1280, 720,  False),
            "1920 × 1080": (1920, 1080, False),
            "2560 × 1440": (2560, 1440, False),
            "Fullscreen":  (1920, 1080, True),
        }
        return mapping.get(s, (1280, 720, False))
