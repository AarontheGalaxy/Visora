#version 330 core

in vec2 in_pos;
in float in_brightness;

uniform float u_bass;

out float v_brightness;
out float v_y;

void main() {
    v_brightness = in_brightness;
    v_y = in_pos.y;
    gl_Position = vec4(in_pos, 0.0, 1.0);
}
