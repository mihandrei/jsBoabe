scene :
    * list of objects
    * lights ()
    * camera (projection matrix)

materials : shaders

object:
    * geometry
    * material ref
    * model matrix
    * optional sub-objects
    * optional bbox 4 hit testing

dynamic geometry:
    * some attribute buffer changes
    ex:
        * dynamic coloring per vertex (color attrib)
        * transparency (index drawelements buffer changes as triangles are sorted)


encapsulate drawelements vs drawarray
and triangle strip vs lines

belog to mesh class because the mesh generates the data for the buffers?
or to they belong to the object? yep it is the object
the object bring together material geometry and these topological info