function meshmain(){
    scene = new T3.Scene('glcanvas');
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



function on_data_loaded_surface(data) {
    surface = JSON.parse(data[0]);

    window.scene = new T3.Scene('glcanvas');
    var simpleMat = new T3.SimpleMaterial(scene);

    var obj = {
        material:simpleMat,
        arrays: {
            aPosition : surface.vertices,
            aColor : surface.normals
        },
        indices: surface.indices.slice(0, 3 * 1000),
        drawingMode: scene.gl.POINTS
    };

    scene.add(obj);
    scene.render();
}

function on_data_loaded_points(data) {
    nii_data = JSON.parse(data[0]);

    window.scene = new T3.Scene('glcanvas');
    var simpleMat = new T3.SimpleMaterial(scene);

    //position and indices are not always required?
    var obj = {
        material:simpleMat,
        arrays: {
            aPosition: nii_data.vertices,
            aColor : nii_data.vals
        },
        //vertices:
        indices: nii_data.indices.slice(0, 10 * 1000),
        drawingMode: scene.gl.POINTS
    };

    scene.add(obj);
    scene.render();
}

function main(){
    // U3.ajaxes(['surface'], on_data_loaded_surface);
    U3.ajaxes(['voxels'], on_data_loaded_points);

}
