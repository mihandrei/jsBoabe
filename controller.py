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
        vertices = read_space_separated_file('data/nii_points.txt')
        values = read_space_separated_file('data/nii_voxels.txt')

        return json.dumps({'vertices': vertices, 'values':values})

