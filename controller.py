from cherrypy import expose, request
import json
from string import Template
import colorsys


def read_space_separated_file(pth):
    with open(pth) as f:
        return f.read().split()


def readf(pth):
    with open(pth) as f:
        return f.read()


def make_pallete():
    N = 196
    rb = [colorsys.hsv_to_rgb(i/float(N), 1, 0.9) for i in xrange(N)]
    for i in xrange(1, N/2, 2):
        rb[i], rb[N/2+i] = rb[N/2+i], rb[i]
    return rb
    # pallete = [
    #     [.90, .20, .20], [.90, .70, .10], [.90, .90, .10], [.30, .50, .10], [.30, .40, .20], [.92, .92, .92],
    #     [.10, .90, .90], [.10, .10, .90], [.50, .50, .20], [.30, .70, .20], [.60, .60, .60], [.95, .05, .05],
    #     [.02, .02, .99], [.05, .99, .50], [.50, .50, .50], [.80, .80, .80], [.16, .60, .90], [.82, .12, .19],
    #     [.90, .77, .10], [.45, .65, .45], [.75, .45, .45], [.25, 32, 42], [.72, .43, .90], [.66, .32, .46],
    # ] * 8


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
        indices = read_space_separated_file('viewerdata/triangles.txt')
        vertices = read_space_separated_file('viewerdata/vertices.txt')
        vertex_mapping = read_space_separated_file('viewerdata/nii_raw_mapping.txt')

        colors = []
        pallete = make_pallete()
        for v in vertex_mapping:
            #if int(v) >= len(pallete):
            #    raise Exception('aaaa '+v)
            colors.extend(pallete[int(v)])

        return json.dumps({'vertices': vertices, 'indices': indices, 'colors' :colors})

    @expose
    def voxels(self):
        vertices = read_space_separated_file('viewerdata/nii_points.txt')
        values = read_space_separated_file('viewerdata/nii_raw_voxels.txt')
        colors = []
        pallete = make_pallete()
        for v in values:
            #if int(v) >= len(pallete):
            #    raise Exception('aaaa '+v)
            colors.extend(pallete[int(v)])

        return json.dumps({'vertices': vertices, 'colors':colors})

