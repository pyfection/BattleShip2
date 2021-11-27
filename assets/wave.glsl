---VERTEX SHADER--- // vertex shader starts here
#ifdef GL_ES
    precision highp float;
#endif

/* Outputs to the fragment shader */
varying vec4 frag_color;
varying vec2 tex_coord0;

/* vertex attributes */
attribute vec2     vPosition;
attribute vec2     vTexCoords0;

/* uniform variables */
uniform mat4       modelview_mat;
uniform mat4       projection_mat;
uniform vec4       color;

void main (void) {
  frag_color = color;
  tex_coord0 = vTexCoords0;
  gl_Position = projection_mat * modelview_mat * vec4(vPosition.xy, 0.0, 1.0);
}


---FRAGMENT SHADER--- // fragment shader starts here
#ifdef GL_ES
precision mediump float;
#endif

uniform vec2 resolution;
uniform float time;

float rand(vec2 co){
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

void main() {
    vec2 st = gl_FragCoord.xy/vec2(32, 32).xy;
    //vec2 st = floor(gl_FragCoord.xy/vec2(4, 4).xy);

    vec3 color = vec3(0.);
    color = vec3(0.0, 0.48, 0.75) / vec3(abs(sin(time+st.x+sin(st.y)))*.5+.5);
    //color = vec3(0.0, 0.48, 0.75) / vec3((abs(sin(time*rand(st)))*.25+.75));

    gl_FragColor = vec4(color,1.0);
}
