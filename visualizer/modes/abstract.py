"""
Abstract plasma mode — numpy software renderer.
Milkdrop-style plasma using sin wave interference patterns.
Rendered at half resolution then upscaled for performance.
"""

import numpy as np


class AbstractMode:
    NAME = "Abstract"
    DESCRIPTION = "Milkdrop-inspired plasma shader"

    def __init__(self, width: int, height: int):
        self._w = width
        self._h = height
        # Precompute half-res coordinate grids once
        hw, hh = width // 2, height // 2
        xx = np.linspace(0.0, 1.0, hw, dtype=np.float32)
        yy = np.linspace(0.0, 1.0, hh, dtype=np.float32)
        self._xx, self._yy = np.meshgrid(xx, yy)
        self._t = 0.0

    def render(self, frame_data, preset: dict) -> np.ndarray:
        self._t += 0.016

        t = self._t
        bass   = float(frame_data.bass)
        mid    = float(frame_data.mid)
        treble = float(frame_data.treble)

        zoom     = float(preset.get("zoom",     1.0))
        rotation = float(preset.get("rotation", 0.3))

        xx = self._xx
        yy = self._yy

        # Centre and apply zoom
        cx = (xx - 0.5) * zoom
        cy = (yy - 0.5) * zoom

        # Soft rotation driven by the rotation param + time
        angle = t * rotation
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        rx = cx * cos_a - cy * sin_a
        ry = cx * sin_a + cy * cos_a

        # Three sin waves — bass / mid / treble modulate amplitude
        v  = np.sin(rx * 10.0 + t       + bass   * 3.0)
        v += np.sin(ry * 8.0  - t * 0.7 + mid    * 2.0)
        v += np.sin((rx + ry) * 6.0 + t * 1.3 + treble * 1.5)
        v  = (v / 3.0 + 1.0) / 2.0          # normalise 0-1

        # Colour mix
        ca = np.array(preset.get("color_a", [0.1, 0.0, 0.5]), dtype=np.float32)
        cb = np.array(preset.get("color_b", [0.0, 1.0, 0.8]), dtype=np.float32)

        v3  = v[:, :, np.newaxis]
        rgb_half = np.clip(ca * (1.0 - v3) + cb * v3, 0.0, 1.0)
        rgb_half = (rgb_half * 255).astype(np.uint8)

        # 2× nearest-neighbour upscale (no PIL needed)
        rgb = np.repeat(np.repeat(rgb_half, 2, axis=0), 2, axis=1)

        # Crop/pad to exact target size
        rgb = rgb[:self._h, :self._w]

        return rgb

    def cleanup(self):
        pass
