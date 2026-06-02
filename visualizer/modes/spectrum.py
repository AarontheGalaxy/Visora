import numpy as np


class SpectrumMode:
    NAME = "Spectrum"
    DESCRIPTION = "Frequency spectrum bars"

    N_BARS = 64

    def __init__(self, width: int, height: int):
        self._w = width
        self._h = height

    def render(self, frame_data, preset: dict) -> np.ndarray:
        rgb = np.zeros((self._h, self._w, 3), dtype=np.uint8)

        spectrum     = frame_data.spectrum                          # 64 floats 0-1
        color_low    = np.array(preset.get("color_low",  [0.1, 0.4, 1.0]), dtype=np.float32)
        color_high   = np.array(preset.get("color_high", [1.0, 0.2, 0.8]), dtype=np.float32)
        mirror       = bool(preset.get("mirror", True))
        height_scale = float(preset.get("height", 0.9))

        n      = self.N_BARS
        bar_w  = self._w // n
        gap    = max(1, bar_w // 8)
        cy     = self._h // 2

        for i, amp in enumerate(spectrum[:n]):
            amp   = float(amp)
            x0    = i * bar_w + gap
            x1    = x0 + bar_w - gap * 2
            if x1 <= x0:
                x1 = x0 + 1

            bar_h = int(amp * height_scale * cy)
            color = np.clip(color_low * (1.0 - amp) + color_high * amp, 0.0, 1.0)
            cu8   = (color * 255).astype(np.uint8)

            if mirror:
                y0 = max(0, cy - bar_h)
                y1 = min(self._h, cy + bar_h)
            else:
                y0 = max(0, self._h - bar_h * 2)
                y1 = self._h

            if y1 > y0:
                rgb[y0:y1, x0:x1] = cu8

        return rgb

    def cleanup(self):
        pass
