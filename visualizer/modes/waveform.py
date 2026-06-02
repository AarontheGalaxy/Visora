import numpy as np
import moderngl


class WaveformMode:
    NAME = "Waveform"
    DESCRIPTION = "Classic oscilloscope-style waveform"

    def __init__(self, ctx: moderngl.Context, shader_dir: str):
        self._ctx = ctx
        with open(f"{shader_dir}/waveform.vert") as f:
            vert = f.read()
        with open(f"{shader_dir}/waveform.frag") as f:
            frag = f.read()
        self._prog = ctx.program(vertex_shader=vert, fragment_shader=frag)

        n = 512
        x = np.linspace(-1.0, 1.0, n, dtype=np.float32)
        y = np.zeros(n, dtype=np.float32)

        vdata = np.column_stack([x, y]).astype(np.float32)
        self._vbo = ctx.buffer(vdata.tobytes())
        self._vao = ctx.simple_vertex_array(self._prog, self._vbo, "in_x", "in_y")

    def render(self, frame_data, preset: dict):
        waveform = frame_data.waveform  # 512 floats -1..1

        color = preset.get("color", [0.2, 0.8, 1.0])
        n = len(waveform)
        x = np.linspace(-1.0, 1.0, n, dtype=np.float32)
        y = np.clip(waveform * preset.get("amplitude", 0.7), -1.0, 1.0).astype(np.float32)

        vdata = np.column_stack([x, y]).astype(np.float32)
        self._vbo.write(vdata.tobytes())

        self._prog["u_color"].value = tuple(color)

        self._ctx.line_width = preset.get("line_width", 2.0)
        self._vao.render(moderngl.LINE_STRIP)

    def cleanup(self):
        self._vbo.release()
        self._vao.release()
        self._prog.release()
