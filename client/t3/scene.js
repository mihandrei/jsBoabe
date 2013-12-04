(function(T3){

function Scene(canvasId){
    this.canvas = document.getElementById(canvasId);
    var gl = this.canvas.getContext("webgl") || this.canvas.getContext("experimental-webgl");
    this.gl = gl;
    this.objects = [];
    this.fps = 10;
    // Near things obscure far things
    gl.depthFunc(gl.LEQUAL);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
    disable_transparency(gl);

    // camera stuff
    gl.viewport(0, 0, this.canvas.clientWidth, this.canvas.clientHeight);
    var aspect = this.canvas.clientWidth / this.canvas.clientHeight;

    this.mProj = mat4.create();
    this.mModelView = mat4.create();
    mat4.scale(this.mModelView, this.mModelView, [0.01, 0.01, 0.01]);
    mat4.translate(this.mModelView, this.mModelView, [0, 0, -4]);
    mat4.perspective(this.mProj, Math.PI/6, aspect, 3 , 5);
}

function enable_transparency(gl){
    gl.disable(gl.DEPTH_TEST);
    gl.enable(gl.BLEND);

}

function disable_transparency(gl){
    gl.enable(gl.DEPTH_TEST);
    gl.disable(gl.BLEND);

}

Scene.prototype.pre_render = function(){

};

// translate obj.arrays to gpu buffers
// add object to scene to be rendered
// obj = {arrays:{name, [data]}, modeview, material}
// the special array indices is required
// maybe standardize some arrays : vertices normals uv ?
// later maybe consolidate buffers and
// let geometry append to an existing buffer
Scene.prototype.add = function(obj) {
    var gl = this.gl;

    function do_buffer(tarray, buffGpuTarget){
        var buff = gl.createBuffer();
        buff.length = tarray.length;
        //this is the curent buffer
        gl.bindBuffer(buffGpuTarget, buff);
        gl.bufferData(buffGpuTarget, tarray, gl.STATIC_DRAW);
        return buff;
    }

    for (var k in obj.arrays) {
        obj.arrays[k] = do_buffer(new Float32Array(obj.arrays[k]), gl.ARRAY_BUFFER);
    }

    if('indices' in obj){
        if(obj.indices.length>65535){
            console.log('indices above 65 535 are not supported!')
        }
        obj.indices = do_buffer(new Uint16Array(obj.indices), gl.ELEMENT_ARRAY_BUFFER);
    }else if('vertices' in obj){
        obj.vertices = obj.arrays[obj.vertices];
    }

    this.objects.push(obj);
};

Scene.prototype.render = function() {
    var gl = this.gl;

    function topology(mat, obj){
        if ('indices' in obj){
            //bind indices buffer
            gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, obj.indices);
            //invoke the program
            gl.drawElements(mat.drawingMode, obj.indices.length, gl.UNSIGNED_SHORT, 0);
        }else if('vertices' in obj){
            gl.bindBuffer(gl.ARRAY_BUFFER, obj.vertices);
            gl.drawArrays(mat.drawingMode, 0, obj.vertices.length/3);
        }
    }

    function custom_draw(mat, obj){
        if ('draw' in obj){
            obj.draw(gl);
            return true;
        }
        // update buffers for dynamic objects
        if ('update' in obj){
            obj.update();
        }
        return false;
    }

    function bind_uniforms(mat){
        // bind common uniforms
        // mv p martrices
        gl.uniformMatrix4fv(mat.uPmatrix, false, this.mProj);
        gl.uniformMatrix4fv(mat.uMVmatrix, false, this.mModelView);

        // bind material uniforms
        for (var unif in mat.uniforms){
            // todo
        }
    }

    function bind_attributes(mat, obj){
        // discover attributes of the program and
        // bind them to obj buffer
        for (var attr in mat.attributes){
            var attrGpuID = mat.attributes[attr];
            gl.enableVertexAttribArray(attrGpuID);
            //use this buffer
            gl.bindBuffer(gl.ARRAY_BUFFER, obj.arrays[attr]);
            //bind that buffer to this attribute
            gl.vertexAttribPointer(attrGpuID, 3, gl.FLOAT, false, 0, 0);
        }
    }

    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    this.pre_render();

    for (var i = 0; i < this.objects.length; i++) {
        var obj = this.objects[i];
        var mat = obj.material;

        gl.useProgram(mat.program);

        if(custom_draw(mat, obj)){
            continue;
        }

        bind_uniforms.call(this, mat);
        bind_attributes.call(this, mat, obj);

//        if ('transparent' in mat){
//            enable_transparency(gl);
//            topology(mat, obj);
//            disable_transparency(gl);
//        }else{
            topology(mat, obj);
//        }
    }

    setTimeout(function(){Scene.prototype.render.apply(scene);}, 1000/this.fps);
};

//? mvp matrix position are not that much materially
function SimpleMaterial(scene){
    var gl = scene.gl;
    this.program = T3.pr.load_program(gl, 'simple.vertex', 'simple.fragment');
    this.uPmatrix = gl.getUniformLocation(this.program, "uPmatrix");
    this.uMVmatrix = gl.getUniformLocation(this.program, "uMVmatrix");
    this.drawingMode = gl.TRIANGLES;//LINE_LOOP;
    //this.transparent = 1;
    this.attributes = {
        aPosition : gl.getAttribLocation(this.program, "aPosition"),
        aColor : gl.getAttribLocation(this.program, "aColor")
    };

    this.uniforms = {
    };
}

function DottyMaterial(scene){
    var gl = scene.gl;
    this.program = T3.pr.load_program(gl, 'dotty.vertex', 'simple.fragment');
    this.uPmatrix = gl.getUniformLocation(this.program, "uPmatrix");
    this.uMVmatrix = gl.getUniformLocation(this.program, "uMVmatrix");
    this.drawingMode = gl.POINTS;

    this.attributes = {
        aPosition : gl.getAttribLocation(this.program, "aPosition")
      , aColor : gl.getAttribLocation(this.program, "aColor")
    };

    this.uniforms = {
    };
}

function LineMaterial(scene){
    var gl = scene.gl;
    this.program = T3.pr.load_program(gl, 'dotty.vertex', 'simple.fragment');
    this.uPmatrix = gl.getUniformLocation(this.program, "uPmatrix");
    this.uMVmatrix = gl.getUniformLocation(this.program, "uMVmatrix");
    this.drawingMode = gl.LINES;

    this.attributes = {
        aPosition : gl.getAttribLocation(this.program, "aPosition")
    };

    this.uniforms = {
    };
}

// todo replace obj ad hoc dict structure with a constructor
// validate that the object is sane
function Object(material, arrays, drawingMode){
    this.material = material;
    this.arrays = [];
    this.indices = null;
    this.vertices = null;
}

// exports here
T3.Scene = Scene;
T3.SimpleMaterial = SimpleMaterial;
T3.DottyMaterial = DottyMaterial;
T3.LineMaterial=LineMaterial;
//list requirements here so that we fail fast if they are missing
})(T3, T3.pr);