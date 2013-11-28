(function(){

function load_program_from_string(gl, vertex_src, frag_src){
    function compile(gl, shader, shader_src){
        gl.shaderSource(shader, shader_src);
        gl.compileShader(shader);

        if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
            console.warn("error compiling shader: " + shader_src + "\n " + gl.getShaderInfoLog(shader));
            throw "CompilationError";
        }
    }
    var vertex = gl.createShader(gl.VERTEX_SHADER);
    var fragment = gl.createShader(gl.FRAGMENT_SHADER);
    compile(gl, vertex, vertex_src);
    compile(gl, fragment, frag_src);

    var program = gl.createProgram();
    gl.attachShader(program, vertex);
    gl.attachShader(program, fragment);
    gl.linkProgram(program);

    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
        console.warn("Unable to initialize the shader program.");
        throw "CompilationError";
    }
    return program;
}

function load_script_tag_text(id) {
    var script = document.getElementById(id);

    if (!script || !script.firstChild){
        console.warn('could not load script tag with id ' + id);
        return null;
    }else{
        return script.firstChild.textContent;
    }
}

function load_program(gl, vertex_id, fragment_id){
    var vsrc = load_script_tag_text(vertex_id);
    var fsrc = load_script_tag_text(fragment_id);
    return load_program_from_string(gl, vsrc, fsrc);
}

// exports here
T3 = {
    pr : {
        load_program:load_program,
        load_program_from_string:load_program_from_string
    }
};

})();
