function main(){
    var scene = new T3.Scene('glcanvas');
    var simpleMat = new T3.SimpleMaterial(scene);
    var mesh = T3.mesh(8,8);

    //position and indices are not always required?
    var obj = {
        material:simpleMat,
        arrays: {
            aPosition : mesh.vertices,
            aColor : mesh.colors,
        },
        //vertices:
        indices: mesh.indices,
        drawingMode: scene.gl.TRIANGLE_STRIP
    };

    scene.add(obj);
    scene.render();
}
