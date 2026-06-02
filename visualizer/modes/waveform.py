import numpy as np


class WaveformMode:
    NAME = "Waveform"
    DESCRIPTION = "Classic oscilloscope-style waveform"

    def __init__(self, width: int, height: int):
        self._w = width
        self._h = height

    def render(self, frame_data, preset: dict) -> np.ndarray:
        rgb = np.zeros((self._h, self._w, 3), dtype=np.uint8)

        waveform  = frame_data.waveform                          # 512 floats -1..1
        color     = np.array(preset.get("color", [0.2, 0.8, 1.0]), dtype=np.float32)
        amplitude = float(preset.get("amplitude", 0.7))
        cu8       = (np.clip(color, 0.0, 1.0) * 255).astype(np.uint8)

        n  = len(waveform)
        xs = (np.arange(n) / n * self._w).astype(np.int32)
        ys = ((0.5 - np.clip(waveform * amplitude, -1.0, 1.0) * 0.45)
              * self._h).astype(np.int32)
        ys = np.clip(ys, 0, self._h - 1)

        # Draw a vertical slice at each x from previous y to current y
        # — fast numpy column fill, no Python per-pixel loop
        for i in range(len(xs) - 1):
            x = int(xs[i])
            if x < 0 or x >= self._w:
                continue
            y0 = int(min(ys[i], ys[i + 1]))
            y1 = int(max(ys[i], ys[i + 1])) + 1
            y0 = max(0, y0)
            y1 = min(self._h, y1)
            rgb[y0:y1, x] = cu8

        return rgb

    def cleanup(self):
        pass
