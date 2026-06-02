import numpy as np
import moderngl


class SpectrumMode:
    NAME = "Spectrum"
    DESCRIPTION = "Frequency spectrum bars"

    N_BARS = 64

    def __init__(self, ctx: moderngl.Context, shader_dir: str):
        self._ctx = ctx
        with open(f"{shader_dir}/bars.vert") as f:
            vert = f.read()
        with open(f"{shader_dir}/bars.frag") as f:
            frag = f.read()
        self._prog = ctx.program(vertex_shader=vert, fragment_shader=frag)

        # Each bar = 2 triangles (6 verts), each vert has (x, y, brightness)
        self._vbo = ctx.buffer(reserve=self.N_BARS * 6 * 3 * 4)
        self._vao = ctx.simple_vertex_array(
            self._prog, self._vbo, "in_pos", "in_brightness"
        )

    def render(self, frame_data, preset: dict):
        spectrum = frame_data.spectrum  # 64 floats 0..1
        bass = frame_data.bass

        color_low = tuple(preset.get("color_low", [0.1, 0.4, 1.0]))
        color_high = tuple(preset.get("color_high", [1.0, 0.2, 0.8]))
        mirror = preset.get("mirror", True)

        n = self.N_BARS
        bar_w = 2.0 / n
        gap = bar_w * 0.15

        verts = []
        for i, amp in enumerate(spectrum):
            x0 = -1.0 + i * bar_w + gap / 2
            x1 = x0 + bar_w - gap
            h = float(amp) * preset.get("height", 0.9)

            if mirror:
                y_bot, y_top = -h, h
            else:
                y_bot, y_top = -1.0, -1.0 + h * 2.0

            brightness = float(amp)
            # Two triangles forming a quad
            for (x, y) in [(x0, y_bot), (x1, y_bot), (x0, y_top),
                           (x1, y_bot), (x1, y_top), (x0, y_top)]:
                verts.extend([x, y, brightness])

        data = np.array(verts, dtype=np.float32)
        self._vbo.write(data.tobytes())

        self._prog["u_color_low"].value = color_low
        self._prog["u_color_high"].value = color_high
        self._prog["u_bass"].value = float(bass)

        self._vao.render(moderngl.TRIANGLES)

    def cleanup(self):
        self._vbo.release()
        self._vao.release()
        self._prog.release()
