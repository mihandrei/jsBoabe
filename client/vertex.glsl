uniform mat4 uPmatrix;
uniform mat4 uMVmatrix;

attribute vec3 aPosition;
attribute vec3 aColor;

varying vec4 vColor;

void main(void) {
    gl_Position = uPmatrix * uMVmatrix * vec4(aPosition, 1);
    vec3 cc = vec3(0.3, 0.3, 0.3) + aColor.rgb;
    vColor = vec4(clamp(cc, 0.0, 1.0), 1.0) ;
}