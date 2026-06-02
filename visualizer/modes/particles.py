import random
import numpy as np


class ParticlesMode:
    NAME = "Particles"
    DESCRIPTION = "Beat-reactive particle system"

    MAX_PARTICLES = 600

    def __init__(self, width: int, height: int):
        self._w = width
        self._h = height
        # Each row: [x, y, vx, vy, life, size]
        self._buf = np.zeros((self.MAX_PARTICLES, 6), dtype=np.float32)
        self._count = 0

    def render(self, frame_data, preset: dict) -> np.ndarray:
        rgb = np.zeros((self._h, self._w, 3), dtype=np.uint8)

        bass  = float(frame_data.bass)
        beat  = frame_data.beat
        rms   = float(frame_data.rms)

        color      = np.array(preset.get("color",      [0.6, 0.3, 1.0]), dtype=np.float32)
        spawn_rate = int(preset.get("spawn_rate", 8))
        gravity    = float(preset.get("gravity",  -0.0005)) * self._h
        decay      = float(preset.get("decay",     0.012))

        # Spawn
        n_spawn = spawn_rate if beat else max(1, int(rms * spawn_rate))
        n_spawn = min(n_spawn, self.MAX_PARTICLES - self._count)

        cx, cy = self._w / 2.0, self._h / 2.0
        for _ in range(n_spawn):
            angle = random.uniform(0.0, 2.0 * np.pi)
            speed = random.uniform(1.0, 5.0) * (1.0 + bass * 3.0) * (self._h / 720.0)
            p = self._buf[self._count]
            p[0] = cx + random.uniform(-self._w * 0.1, self._w * 0.1)
            p[1] = cy + random.uniform(-self._h * 0.05, self._h * 0.05)
            p[2] = np.cos(angle) * speed
            p[3] = np.sin(angle) * speed + speed * 0.3
            p[4] = 1.0
            p[5] = random.uniform(3.0, 8.0) * (1.0 + bass)
            self._count += 1

        if self._count == 0:
            return rgb

        alive = self._buf[:self._count]

        # Physics update (vectorised)
        alive[:, 0] += alive[:, 2]          # x += vx
        alive[:, 1] += alive[:, 3]          # y += vy
        alive[:, 3] += gravity              # vy += gravity
        alive[:, 4] -= decay               # life -= decay

        mask = alive[:, 4] > 0.0
        n_alive = int(mask.sum())
        if n_alive < self._count:
            self._buf[:n_alive] = alive[mask]
            self._count = n_alive
            alive = self._buf[:self._count]

        # Draw
        cu8 = (np.clip(color, 0.0, 1.0) * 255).astype(np.uint8)
        for i in range(self._count):
            x   = int(alive[i, 0])
            y   = int(alive[i, 1])
            lif = float(alive[i, 4])
            r   = max(1, int(alive[i, 5] * lif))

            x0, x1 = max(0, x - r), min(self._w, x + r + 1)
            y0, y1 = max(0, y - r), min(self._h, y + r + 1)
            if x1 > x0 and y1 > y0:
                c = (cu8 * lif).astype(np.uint8)
                rgb[y0:y1, x0:x1] = np.maximum(rgb[y0:y1, x0:x1], c)

        return rgb

    def cleanup(self):
        pass
