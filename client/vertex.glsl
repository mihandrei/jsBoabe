uniform mat4 uPmatrix;
uniform mat4 uMVmatrix;

attribute vec3 aPosition;
attribute vec3 aColor;

varying vec4 vColor;

void main(void) {
    gl_Position = uPmatrix * uMVmatrix * vec4(aPosition, 1);
    vColor = vec4(0.1, aColor.yz, 0.5);
}