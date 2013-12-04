function onkey(evt){
    switch (evt.keyCode){
        case 38: rot_u(); break;
        case 40: rot_d(); break;
        case 37: rot_l(); break;
        case 39: rot_r(); break;
        case 88: toggle_vox(); break;
        case 87: tr_w(); break;
        case 83: tr_s(); break;
        case 80: toggle_persp(); break;
    }
}

function bind_events(){
    document.getElementById('wbtn').onclick = tr_w;
    document.getElementById('sbtn').onclick = tr_s;
    document.getElementById('xbtn').onclick = toggle_vox;
    document.getElementById('ubtn').onclick = rot_u;
    document.getElementById('dbtn').onclick = rot_d;
    document.getElementById('lbtn').onclick = rot_l;
    document.getElementById('rbtn').onclick = rot_r;
    document.getElementById('pbtn').onclick = toggle_persp;
    window.onkeydown = onkey;
}

function rot_u(){
    mat4.rotate(scene.mModelView, scene.mModelView, Math.PI/2, [1,0,0]);
}
function rot_d(){
    mat4.rotate(scene.mModelView, scene.mModelView, -Math.PI/2, [1,0,0]);
}
function rot_l(){
    mat4.rotate(scene.mModelView, scene.mModelView, Math.PI/2, [0,1,0]);
}
function rot_r(){
    mat4.rotate(scene.mModelView, scene.mModelView, -Math.PI/2, [0,1,0]);
}
function toggle_vox(){
    if('draw' in scene.objects[0]){
        delete scene.objects[0].draw
    }else{
        scene.objects[0].draw = function(){};
    }
}
function tr_w(){
    mat4.translate(scene.mModelView, scene.mModelView, [0,0,-0.05]);
}
function tr_s(){
    mat4.translate(scene.mModelView, scene.mModelView, [0,0, +0.05]);
}

var slicing = false;

function toggle_persp(){
    // slicing frustum
    var aspect = scene.canvas.clientWidth / scene.canvas.clientHeight;
    mat4.identity(scene.mProj);
    slicing = !slicing;

    if(slicing){
        mat4.perspective(scene.mProj, Math.PI/6, aspect, 3 , 3.01);
    }else{
        mat4.perspective(scene.mProj, Math.PI/6, aspect, 3 , 5);
    }
}

function on_data_loaded(data) {
    notBusy();
    window.surface = JSON.parse(data[0]);
    window.voxels = JSON.parse(data[1]);
    window.scene = new T3.Scene('glcanvas');
    bind_events();
    scene.fps = 5;

//    scene.pre_render= function(){
//        mat4.rotate(this.mModelView, this.mModelView, 0.01, [0, 1, 0.5]);
//    };

    var dottyMat = new T3.DottyMaterial(scene);
    var simpleMat = new T3.SimpleMaterial(scene);
    var lineMat= new T3.LineMaterial(scene);

    var xoy_mesh ={
        material: lineMat,
        arrays:{
            aPosition:[
                0,0,0, 100,0,0, 0,100,0, 0,0,100
            ]
        },
        indices:[0,1,0,2,0,3]
    };

    var voxel_object = {
        material:dottyMat,
        arrays: {
            aPosition: voxels.vertices,
            aColor:voxels.colors
        },
        vertices: 'aPosition'
    };

    var surface_object = {
        material:simpleMat,
        arrays: {
            aPosition: surface.vertices,
            aColor : surface.normals
        },
        indices: surface.indices.slice(0,350*1000)
    };

    scene.add(surface_object);
    scene.add(voxel_object);
    scene.add(xoy_mesh);

    scene.render();
}

function busy(){
    var spinner = document.getElementById('spinner');
    spinner.style.visibility = 'visible';
}

function notBusy(){
    var spinner = document.getElementById('spinner');
    spinner.style.visibility = 'hidden';
}

function main(){
    busy();
    var d = [
        'surface'
        ,
        'voxels'
    ];
    U3.ajaxes(d, on_data_loaded);


}
