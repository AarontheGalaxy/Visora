#version 330 core

in float v_brightness;
in float v_y;

uniform vec3 u_color_low;
uniform vec3 u_color_high;
uniform float u_bass;

out vec4 f_color;

void main() {
    float t = clamp(v_y * 0.5 + 0.5, 0.0, 1.0);
    vec3 col = mix(u_color_low, u_color_high, t);
    col += u_bass * 0.3 * vec3(1.0, 0.4, 0.1);
    f_color = vec4(col * v_brightness, 1.0);
}
