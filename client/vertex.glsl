uniform mat4 uPmatrix;
uniform mat4 uMVmatrix;

attribute vec3 aPosition;
// attribute vec3 aColor;
attribute float aColor;

varying vec3 vColor;

void main(void) {
    gl_Position = uPmatrix * uMVmatrix * vec4(aPosition, 1);
    gl_PointSize = 1.0;
    vColor = vec3(aColor/128.0,0,0);
}