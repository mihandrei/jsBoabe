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
    window.surface = JSON.parse(data[0]);

    window.scene = new T3.Scene('glcanvas');
    var simpleMat = new T3.SimpleMaterial(scene);

    var obj = {
        material:simpleMat,
        arrays: {
            aPosition : surface.vertices,
            aColor : surface.normals
        },
        indices: surface.indices.slice(0,200000),
        drawingMode: scene.gl.TRIANGLES
    };

    scene.add(obj);
    scene.render();
}

function on_data_loaded_points(data) {
    window.nii_data = JSON.parse(data[0]);

    window.scene = new T3.Scene('glcanvas');
    var simpleMat = new T3.DottyMaterial(scene);

    //position and indices are not always required?
    var obj = {
        material:simpleMat,
        arrays: {
            aPosition: nii_data.vertices
        },
        //vertices:
        indices: nii_data.indices,
        drawingMode: scene.gl.POINTS
    };

    scene.add(obj);
    scene.render();
}

function on_data_loaded_surface_and_points(data) {
    window.surface = JSON.parse(data[0]);
    window.voxels = JSON.parse(data[1]);
    window.scene = new T3.Scene('glcanvas');

    var dottyMat = new T3.DottyMaterial(scene);
    var simpleMat = new T3.SimpleMaterial(scene);

    var voxel_object = {
        material:dottyMat,
        arrays: {
            aPosition: voxels.vertices
        },
        indices: voxels.indices.slice(0,900*1000)
    };

    var surface_object = {
        material:simpleMat,
        arrays: {
            aPosition: surface.vertices,
            aColor : surface.normals
        },
        indices: surface.indices.slice(0,300*1000)
    };

    scene.add(voxel_object);
    scene.add(surface_object);

    scene.render();
}

function main(){
//    U3.ajaxes(['surface'], on_data_loaded_surface);
//    U3.ajaxes(['voxels'], on_data_loaded_points);
    U3.ajaxes(['surface', 'voxels'], on_data_loaded_surface_and_points);
}
