"""
Abstract / Milkdrop-style mode — software renderer.

Implements the core Milkdrop rendering pipeline in numpy:
  fDecay   → frame buffer multiplied each tick (creates glowing trails)
  zoom     → radial zoom from center via inverse-warp sampling
  rot      → slow rotation driven by preset + time
  warp     → sinusoidal mesh distortion
  color wash → audio-reactive colour layer added on top

These are the same parameters used by real .milk presets.
Rendered at half resolution (faster), then 2× upscaled for display.
"""

import numpy as np


class AbstractMode:
    NAME = "Abstract"
    DESCRIPTION = "Milkdrop-inspired plasma with trail / zoom / warp"

    def __init__(self, width: int, height: int):
        self._w = width
        self._h = height

        # Half-res buffer — renders here, upscaled on output
        hw, hh = width // 2, height // 2
        self._hw = hw
        self._hh = hh
        self._buf = np.zeros((hh, hw, 3), dtype=np.float32)

        # Precomputed grids (half-res, absolute pixel coords)
        yy, xx = np.mgrid[0:hh, 0:hw].astype(np.float32)
        self._xx = xx          # 0 … hw-1
        self._yy = yy          # 0 … hh-1
        # Normalised -1 … 1
        self._nx = (xx - hw / 2) / (hw / 2)
        self._ny = (yy - hh / 2) / (hh / 2)

        self._t = 0.0

    # ------------------------------------------------------------------

    def render(self, frame_data, preset: dict) -> np.ndarray:
        self._t += 0.016

        t     = self._t
        bass  = float(frame_data.bass)
        mid   = float(frame_data.mid)
        treble = float(frame_data.treble)
        rms   = float(frame_data.rms)
        beat  = frame_data.beat

        # ------ Preset parameters (mirror real .milk variables) ------
        zoom   = float(preset.get("zoom",     1.05))
        rot    = float(preset.get("rotation", 0.3))
        decay  = float(preset.get("decay",    0.95))
        warp   = float(preset.get("warp",     0.3))

        ca = np.array(preset.get("color_a", [0.05, 0.0,  0.4]), dtype=np.float32)
        cb = np.array(preset.get("color_b", [0.0,  1.0,  0.7]), dtype=np.float32)

        cx, cy = self._hw / 2.0, self._hh / 2.0

        # ------ 1. Warp-sample the previous frame --------------------
        #  Inverse-warp: for each destination pixel, find where it
        #  came from in the previous frame.  This gives zoom + rotation
        #  for "free" without any explicit copy.

        zoom_eff = zoom + bass * 0.04          # bass slightly expands
        angle    = t * rot * 0.5

        dx = (self._xx - cx) / zoom_eff
        dy = (self._yy - cy) / zoom_eff

        cos_a, sin_a = float(np.cos(angle)), float(np.sin(angle))
        src_x = cx + dx * cos_a - dy * sin_a
        src_y = cy + dx * sin_a + dy * cos_a

        # Add sinusoidal warp (mirrors fWarpScale in .milk)
        if warp > 0:
            warp_amt = warp * 0.015
            src_x += np.sin(self._ny * 4.0 + t * 1.1) * self._hw * warp_amt
            src_y += np.cos(self._nx * 3.0 + t * 0.9) * self._hh * warp_amt

        src_x = np.clip(src_x, 0, self._hw - 1).astype(np.int32)
        src_y = np.clip(src_y, 0, self._hh - 1).astype(np.int32)

        # Sample + apply decay (fDecay)
        self._buf = self._buf[src_y, src_x] * decay

        # ------ 2. Audio-reactive colour layer -----------------------
        #  Three sine waves driven by bass / mid / treble
        nx, ny = self._nx, self._ny

        v  = np.sin(nx * 6.0 + t        + bass   * 2.5)
        v += np.sin(ny * 5.0 - t * 0.7  + mid    * 1.8)
        v += np.sin((nx + ny) * 4.0 + t * 1.3 + treble)
        v  = (v / 3.0 + 1.0) / 2.0          # 0 … 1

        intensity = rms * 1.8 + bass * 0.25
        if beat:
            intensity += 0.4

        v3        = v[:, :, np.newaxis]
        color_add = (ca * (1.0 - v3) + cb * v3) * 255.0 * intensity

        self._buf = np.clip(self._buf + color_add, 0.0, 255.0)

        # ------ 3. Upscale 2× and return -----------------------------
        out = np.repeat(np.repeat(self._buf.astype(np.uint8), 2, axis=0),
                        2, axis=1)
        return out[:self._h, :self._w]

    def cleanup(self):
        self._buf[:] = 0
