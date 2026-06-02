#version 330 core

in float v_life;

uniform vec3 u_color;

out vec4 f_color;

void main() {
    vec2 coord = gl_PointCoord - vec2(0.5);
    float dist = length(coord);
    if (dist > 0.5) discard;
    float alpha = (1.0 - dist * 2.0) * v_life;
    f_color = vec4(u_color, alpha);
}
