import numpy as np
import moderngl
import random


MAX_PARTICLES = 2000


class ParticlesMode:
    NAME = "Particles"
    DESCRIPTION = "Beat-reactive particle system"

    def __init__(self, ctx: moderngl.Context, shader_dir: str):
        self._ctx = ctx
        with open(f"{shader_dir}/particles.vert") as f:
            vert = f.read()
        with open(f"{shader_dir}/particles.frag") as f:
            frag = f.read()
        self._prog = ctx.program(vertex_shader=vert, fragment_shader=frag)

        # Each particle: x, y, vx, vy, life, size
        dtype = np.dtype([
            ("pos", np.float32, 2),
            ("vel", np.float32, 2),
            ("life", np.float32),
            ("size", np.float32),
        ])
        self._particles = np.zeros(MAX_PARTICLES, dtype=dtype)
        self._count = 0

        # GPU buffer: pos(2) + life(1) + size(1)
        self._vbo = ctx.buffer(reserve=MAX_PARTICLES * 4 * 4)
        self._vao = ctx.simple_vertex_array(
            self._prog, self._vbo, "in_pos", "in_life", "in_size"
        )

    def render(self, frame_data, preset: dict):
        bass = frame_data.bass
        beat = frame_data.beat
        rms = frame_data.rms

        color = tuple(preset.get("color", [0.6, 0.3, 1.0]))
        spawn_rate = preset.get("spawn_rate", 8)
        gravity = preset.get("gravity", -0.0005)
        decay = preset.get("decay", 0.012)

        # Spawn particles on beat or continuously based on RMS
        n_spawn = spawn_rate if beat else max(1, int(rms * spawn_rate))
        n_spawn = min(n_spawn, MAX_PARTICLES - self._count)

        for _ in range(n_spawn):
            if self._count >= MAX_PARTICLES:
                break
            p = self._particles[self._count]
            p["pos"] = [random.uniform(-0.8, 0.8), random.uniform(-0.3, 0.3)]
            angle = random.uniform(0, 2 * np.pi)
            speed = random.uniform(0.002, 0.015) * (1 + bass * 3)
            p["vel"] = [np.cos(angle) * speed, np.sin(angle) * speed + 0.008]
            p["life"] = 1.0
            p["size"] = random.uniform(3.0, 8.0) * (1 + bass)
            self._count += 1

        # Update
        alive = []
        for i in range(self._count):
            p = self._particles[i]
            p["pos"][0] += p["vel"][0]
            p["pos"][1] += p["vel"][1]
            p["vel"][1] += gravity
            p["life"] -= decay
            if p["life"] > 0:
                alive.append(i)

        if alive:
            self._particles[:len(alive)] = self._particles[alive]
        self._count = len(alive)

        if self._count == 0:
            return

        # Pack GPU data
        pts = self._particles[:self._count]
        gpu = np.empty(self._count * 4, dtype=np.float32)
        gpu[0::4] = pts["pos"][:, 0]
        gpu[1::4] = pts["pos"][:, 1]
        gpu[2::4] = pts["life"]
        gpu[3::4] = pts["size"]

        self._vbo.write(gpu.tobytes())
        self._prog["u_color"].value = color
        self._prog["u_beat"].value = 1.0 if beat else 0.0

        self._ctx.enable(moderngl.BLEND)
        self._ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE
        self._vao.render(moderngl.POINTS, vertices=self._count)
        self._ctx.disable(moderngl.BLEND)

    def cleanup(self):
        self._vbo.release()
        self._vao.release()
        self._prog.release()
