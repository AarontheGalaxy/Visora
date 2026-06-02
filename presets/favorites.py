"""
Favorites system.
Stores favorited preset names persistently in ~/.visora/favorites.json.
"""

import json
import os
import tempfile
from datetime import datetime

FAVORITES_PATH = os.path.join(os.path.expanduser("~"), ".visora", "favorites.json")


class FavoritesManager:
    def __init__(self):
        os.makedirs(os.path.dirname(FAVORITES_PATH), exist_ok=True)
        self._favorites: list[dict] = self._load()

    # ------------------------------------------------------------------

    def add(self, preset_name: str, mode: str):
        """Add a preset to favorites if not already there."""
        if self.is_favorite(preset_name):
            return
        self._favorites.append({
            "name": preset_name,
            "mode": mode,
            "added_at": datetime.now().isoformat(),
        })
        self._save()

    def remove(self, preset_name: str):
        self._favorites = [f for f in self._favorites if f["name"] != preset_name]
        self._save()

    def toggle(self, preset_name: str, mode: str) -> bool:
        """Toggle favorite status. Returns True if now a favorite."""
        if self.is_favorite(preset_name):
            self.remove(preset_name)
            return False
        self.add(preset_name, mode)
        return True

    def is_favorite(self, preset_name: str) -> bool:
        return any(f["name"] == preset_name for f in self._favorites)

    @property
    def all(self) -> list[dict]:
        """Returns list of favorite dicts: {name, mode, added_at}."""
        return list(self._favorites)

    @property
    def names(self) -> list[str]:
        return [f["name"] for f in self._favorites]

    def clear(self):
        self._favorites = []
        self._save()

    # ------------------------------------------------------------------

    def _load(self) -> list[dict]:
        if not os.path.exists(FAVORITES_PATH):
            return []
        try:
            with open(FAVORITES_PATH, encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def _save(self):
        dir_ = os.path.dirname(FAVORITES_PATH)
        fd, tmp = tempfile.mkstemp(dir=dir_, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(self._favorites, f, indent=2)
            os.replace(tmp, FAVORITES_PATH)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
