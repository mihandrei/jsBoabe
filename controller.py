from cherrypy import expose, request
import json
from string import Template
import svmap

def read_space_separated_file(pth):
    with open(pth) as f:
        return f.read().split()

def readf(pth):
    with open(pth) as f:
        return f.read()

class Main(object):

    @expose
    def index(self):
        templ = Template(readf('index.html'))
        vsrc = readf('client/vertex.glsl')
        fsrc = readf('client/fragment.glsl')
        vdottysrc = readf('client/dotty.glsl')
        return templ.substitute(vshader=vsrc, fshader=fsrc, vdotty=vdottysrc)

    @expose
    def surface(self):
        indices = read_space_separated_file('data/triangles.txt')
        vertices = read_space_separated_file('data/vertices.txt')
        normals = read_space_separated_file('data/vertex_normals.txt')
        return json.dumps({'vertices': vertices, 'normals': normals, 'indices': indices})

    @expose
    def voxels(self):
        with open('data/nii_points') as f:
            vertices = f.read()
        with open('data/nii_vox') as f:
            vals = f.read()
        return '{"vertices": [%s], "indices": %s}' % (vertices[:-1], json.dumps(range(len(vertices)/3/10)))
