#version 330 core

in vec2 in_pos;
in float in_life;
in float in_size;

uniform float u_beat;

out float v_life;

void main() {
    v_life = in_life;
    float sz = in_size * (1.0 + u_beat * 2.0);
    gl_PointSize = sz;
    gl_Position = vec4(in_pos, 0.0, 1.0);
}
