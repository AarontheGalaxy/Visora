import numpy as np
import moderngl


class AbstractMode:
    NAME = "Abstract"
    DESCRIPTION = "Milkdrop-inspired plasma shader"

    def __init__(self, ctx: moderngl.Context, shader_dir: str):
        self._ctx = ctx
        with open(f"{shader_dir}/abstract.vert") as f:
            vert = f.read()
        with open(f"{shader_dir}/abstract.frag") as f:
            frag = f.read()
        self._prog = ctx.program(vertex_shader=vert, fragment_shader=frag)

        # Full-screen quad
        quad = np.array([
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
             1.0,  1.0,
        ], dtype=np.float32)
        self._vbo = ctx.buffer(quad.tobytes())
        self._vao = ctx.simple_vertex_array(self._prog, self._vbo, "in_pos")
        self._time = 0.0

    def render(self, frame_data, preset: dict):
        self._time += 0.016  # ~60fps step

        color_a = tuple(preset.get("color_a", [0.1, 0.0, 0.5]))
        color_b = tuple(preset.get("color_b", [0.0, 1.0, 0.8]))
        zoom = float(preset.get("zoom", 1.0))
        rotation = float(preset.get("rotation", 0.3))

        self._prog["u_time"].value = self._time
        self._prog["u_bass"].value = float(frame_data.bass)
        self._prog["u_mid"].value = float(frame_data.mid)
        self._prog["u_treble"].value = float(frame_data.treble)
        self._prog["u_color_a"].value = color_a
        self._prog["u_color_b"].value = color_b
        self._prog["u_zoom"].value = zoom
        self._prog["u_rotation"].value = rotation

        self._vao.render(moderngl.TRIANGLE_STRIP)

    def cleanup(self):
        self._vbo.release()
        self._vao.release()
        self._prog.release()
