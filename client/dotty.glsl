uniform mat4 uPmatrix;
uniform mat4 uMVmatrix;

attribute vec3 aPosition;
attribute vec4 aColor;
varying vec4 vColor;

void main(void) {
    gl_Position = uPmatrix * uMVmatrix * vec4(aPosition, 1);
    gl_PointSize = 2.0;
//    vColor = vec4( vec3(0.6, 0.6, 0.05) + aPosition/vec3(100, 100, 600), 1.0);
    vColor = aColor;
}