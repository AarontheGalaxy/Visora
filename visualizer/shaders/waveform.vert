#version 330 core

in float in_x;
in float in_y;

uniform vec2 u_resolution;
uniform vec3 u_color;

out vec3 v_color;

void main() {
    v_color = u_color;
    gl_Position = vec4(in_x, in_y, 0.0, 1.0);
}
