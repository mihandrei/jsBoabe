(function(T3){

function Scene(canvasId){
    this.canvas = document.getElementById(canvasId);
    var gl = this.canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
    this.gl = gl;
    this.objects = [];

    gl.enable(gl.DEPTH_TEST);
    // Near things obscure far things
    gl.depthFunc(gl.LEQUAL);
}


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
        obj.indices = do_buffer(new Uint16Array(obj.indices), gl.ELEMENT_ARRAY_BUFFER);
    }else if('vertices' in obj){
        obj.vertices = do_buffer(new Float32Array(obj.vertices), gl.ARRAY_BUFFER);
    }

    this.objects.push(obj);
};

Scene.prototype.render = function() {
    var gl = this.gl;
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

    for (var i = 0; i < this.objects.length; i++) {
        var obj = this.objects[i];
        var mat = obj.material;

        gl.useProgram(mat.program);

        // custom draw
        // if ('draw' in obj){
        //     obj.draw(gl);
        //     continue;
        // }

        // update buffers for dynamic objects
        if ('update' in obj){
            obj.update();
        }

        // bind common uniforms
        // lights
        // mv p martrices

        // bind uniforms
        for (var unif in mat.uniforms){
            //obj.unif
        }

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

        if ('indices' in obj){
            //bind indices buffer
            gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, obj.indices);
            //invoke the program
            gl.drawElements(obj.drawingMode, obj.indices.length, gl.UNSIGNED_SHORT, 0);
        }else if('vertices' in obj){
            gl.bindBuffer(gl.ARRAY_BUFFER, obj.vertices);
            gl.drawArrays(obj.drawingMode, obj.vertices.length, gl.FLOAT, 0);
        }

    }
};

function SimpleMaterial(scene){
    var gl = scene.gl;
    this.program = T3.pr.load_program(gl, 'simple.vertex', 'simple.fragment');
    this.attributes = {
        aPosition : gl.getAttribLocation(this.program, "aPosition"),
        aColor : gl.getAttribLocation(this.program, "aColor")
    };
    this.uniforms = {};
}

// todo replace obj ad hoc dict structure with a constructor
// validate that the object is sane
function Object(material, arrays, drawingMode){
    this.material = material;
    this.arrays = [];
    this.indices = null;
    this.vertices = null;
    this.drawingMode = drawingMode;
}

// exports here
T3.Scene = Scene;
T3.SimpleMaterial = SimpleMaterial;

//list requirements here so that we fail fast if they are missing
})(T3, T3.pr);