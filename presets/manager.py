"""
Preset manager.
Handles built-in presets, user-created presets, and .milk file import
(compatible with projectM/Milkdrop preset format).
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Any

# Milkdrop variables we recognise and map to shader params.
# Unknown keys from .milk files are silently discarded (SEC-2 fix).
_MILK_ALLOWED_KEYS = frozenset({
    "zoom", "rot", "zoomexp", "decay", "warp",
    "r", "g", "b", "r2", "g2", "b2",
    "cx", "cy", "dx", "dy",
    "sx", "sy", "wave_r", "wave_g", "wave_b", "wave_a",
    "wave_mystery", "wave_mode", "wave_scale",
})

BUILTIN_DIR = os.path.join(os.path.dirname(__file__), "builtin")
USER_DIR = os.path.join(os.path.expanduser("~"), ".visora", "presets")


@dataclass
class Preset:
    """A complete visualization preset."""
    name: str
    mode: str                          # Waveform | Spectrum | Particles | Abstract
    params: dict[str, Any] = field(default_factory=dict)
    description: str = ""
    author: str = ""
    builtin: bool = False

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Preset":
        known = {"name", "mode", "params", "description", "author", "builtin"}
        filtered = {k: v for k, v in d.items() if k in known}
        return Preset(**filtered)

    @staticmethod
    def from_milk(path: str) -> "Preset":
        """
        Import a .milk (Milkdrop) preset.
        Only whitelisted variable names are accepted (SEC-2).
        Path must resolve to an existing file — no traversal possible because
        the caller (import_milk) validates the resolved path first.
        """
        safe_name = os.path.splitext(os.path.basename(path))[0]
        params: dict[str, float] = {}

        with open(path, encoding="utf-8", errors="ignore") as f:
            content = f.read()

        for line in content.splitlines():
            line = line.strip()
            if "=" not in line or line.startswith("per_") or line.startswith("warp"):
                continue
            key, _, val = line.partition("=")
            key = key.strip().lower()
            if key not in _MILK_ALLOWED_KEYS:
                continue  # discard unknown keys
            val = val.strip().rstrip(";")
            try:
                params[key] = float(val)
            except ValueError:
                pass  # skip non-numeric values

        mapped: dict[str, Any] = {
            "zoom":     max(0.1, min(params.get("zoom", 1.0), 5.0)),
            "rotation": max(-5.0, min(params.get("rot", 0.3), 5.0)),
            "color_a":  [params.get("r", 0.1), params.get("g", 0.0), params.get("b", 0.5)],
            "color_b":  [params.get("r2", 0.0), params.get("g2", 1.0), params.get("b2", 0.8)],
        }

        return Preset(name=safe_name, mode="Abstract", params=mapped,
                      description=f"Imported from {safe_name}.milk")


class PresetManager:
    def __init__(self):
        os.makedirs(USER_DIR, exist_ok=True)
        self._presets: dict[str, Preset] = {}
        self._load_builtins()
        self._load_user_presets()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def all_presets(self) -> list[Preset]:
        return list(self._presets.values())

    @property
    def builtin_presets(self) -> list[Preset]:
        return [p for p in self._presets.values() if p.builtin]

    @property
    def user_presets(self) -> list[Preset]:
        return [p for p in self._presets.values() if not p.builtin]

    def get(self, name: str) -> Preset | None:
        return self._presets.get(name)

    def save_user_preset(self, preset: Preset):
        preset.builtin = False
        self._presets[preset.name] = preset
        path = os.path.join(USER_DIR, _safe_filename(preset.name) + ".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(preset.to_dict(), f, indent=2)

    def delete_user_preset(self, name: str) -> bool:
        preset = self._presets.get(name)
        if preset is None or preset.builtin:
            return False
        del self._presets[name]
        path = os.path.join(USER_DIR, _safe_filename(name) + ".json")
        if os.path.exists(path):
            os.remove(path)
        return True

    def import_milk(self, path: str) -> Preset:
        # SEC-1: resolve symlinks and verify the file actually exists and
        # has a .milk extension before passing to the parser.
        resolved = os.path.realpath(path)
        if not os.path.isfile(resolved):
            raise FileNotFoundError(f"Preset file not found: {path}")
        if not resolved.lower().endswith(".milk"):
            raise ValueError("Only .milk files can be imported via this method.")
        preset = Preset.from_milk(resolved)
        self.save_user_preset(preset)
        return preset

    def presets_for_mode(self, mode: str) -> list[Preset]:
        return [p for p in self._presets.values() if p.mode == mode]

    # ------------------------------------------------------------------

    def _load_builtins(self):
        if not os.path.isdir(BUILTIN_DIR):
            return
        for fname in os.listdir(BUILTIN_DIR):
            if fname.endswith(".json"):
                path = os.path.join(BUILTIN_DIR, fname)
                try:
                    with open(path, encoding="utf-8") as f:
                        d = json.load(f)
                    p = Preset.from_dict(d)
                    p.builtin = True
                    self._presets[p.name] = p
                except Exception:
                    pass

    def _load_user_presets(self):
        for fname in os.listdir(USER_DIR):
            if fname.endswith(".json"):
                path = os.path.join(USER_DIR, fname)
                try:
                    with open(path, encoding="utf-8") as f:
                        d = json.load(f)
                    p = Preset.from_dict(d)
                    p.builtin = False
                    self._presets[p.name] = p
                except Exception:
                    pass


def _safe_filename(name: str) -> str:
    """Strip path separators and dots to prevent directory traversal."""
    safe = os.path.basename(name).replace("..", "").strip(". ")
    return safe or "unnamed_preset"
