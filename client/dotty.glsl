uniform mat4 uPmatrix;
uniform mat4 uMVmatrix;

attribute vec3 aPosition;

varying vec4 vColor;

void main(void) {
    gl_Position = uPmatrix * uMVmatrix * vec4(aPosition, 1);
    gl_PointSize = 2.0;
    vColor = vec4( aPosition/vec3(60,60,60), 1);
}