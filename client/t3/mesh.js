(function(T3){

function mesh(DX, DY) {
    //draw a mesh
    var vertices = [];
    var colors = [];
    var indices = [];

    var i, j;
    //vertices
    for (j = 0; j <= DY; j++) {
        for (i = 0; i <= DX; i++) {
            vertices.push(i, j, 0);
        }
    }

    //colors
    for (i = 0; i < vertices.length/3; i++) {
        colors.push(Math.random(), Math.random(), 0.1);
    }

    var currentidx, nextrowidx;
    // indices
    // todo: check winding
    for (j = 0; j < DY; j++) {
        //degenerate triangle
        indices.push((DX + 1) * j);
        for (i = 0; i <= DX; i++) {
            currentidx = i + (DX + 1) * j;
            nextrowidx = currentidx + (DX + 1);
            indices.push(currentidx);
            indices.push(nextrowidx);
        }
        //degenerate triangle at strip end
        indices.push(nextrowidx);
    }
    return {vertices:vertices, colors:colors, indices:indices};
}

T3.mesh = mesh;

})(T3, T3.Scene);
