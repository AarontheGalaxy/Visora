#version 330 core

in vec2 v_uv;

uniform float u_time;
uniform float u_bass;
uniform float u_mid;
uniform float u_treble;
uniform vec3 u_color_a;
uniform vec3 u_color_b;
uniform float u_zoom;
uniform float u_rotation;

out vec4 f_color;

#define PI 3.14159265359

vec2 rotate(vec2 p, float angle) {
    float c = cos(angle), s = sin(angle);
    return vec2(c * p.x - s * p.y, s * p.x + c * p.y);
}

float plasma(vec2 uv, float t) {
    float v = sin(uv.x * 10.0 + t);
    v += sin(uv.y * 10.0 + t * 0.7);
    v += sin((uv.x + uv.y) * 10.0 + t * 1.3);
    float cx = uv.x + 0.5 * sin(t * 0.5);
    float cy = uv.y + 0.5 * cos(t * 0.3);
    v += sin(sqrt(cx * cx + cy * cy + 1.0) * 10.0 - t);
    return v;
}

void main() {
    vec2 uv = v_uv - 0.5;

    // Bass-driven zoom warp
    float zoom = u_zoom + u_bass * 0.4;
    uv /= zoom;

    // Mid-driven rotation
    uv = rotate(uv, u_time * u_rotation + u_mid * 0.5);

    float t = u_time * 0.8;
    float p = plasma(uv, t);

    // Treble adds high-frequency shimmer
    p += u_treble * sin(uv.x * 80.0 + t * 5.0) * 0.15;

    float n = (p + 4.0) / 8.0; // normalize to 0-1
    vec3 col = mix(u_color_a, u_color_b, n);

    // Beat flash
    col += u_bass * 0.2 * vec3(1.0, 0.6, 0.2);

    f_color = vec4(col, 1.0);
}
