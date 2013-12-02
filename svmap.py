"""
This script maps each vertex of a surface to a region.

voxels
    Volumetric data mapping a voxel to a region code.
vertices
    Verices assumed to be from a surface that is compatible with the
    volume described by voxels
"""
import numpy as np
import nibabel
from collections import Counter

class Mapper(object):
    def __init__(self, voxels, vertices, affine):
        self.voxels = voxels
        self.vertices = vertices
        self.affine = affine
        self.invaffine = np.linalg.inv(self.affine)

    def stats(self):
        print 'voxels'
        counts = Counter(self.voxels.flat)
        print 'unique values %s' % len(counts)

        # for kv in counts.iteritems():
            # print '%s : %s' % kv

        print 'voxel positions after affine transform'
        print '000 - %s' % self.affine.dot([0,0,0,1])
        print '111 - %s' % self.affine.dot(list(self.voxels.shape) + [1])

        print 'vertices positions'
        print 'x y z mins %s' %  np.min(self.vertices, axis=0)
        print 'x y z maxs %s' %  np.max(self.vertices, axis=0)

    def vertices2voxel_indices(self):
        onecolumn = np.ones((self.vertices.shape[0], 1))
        # we add a homogen coord 2 all vertices
        affine_vertices = np.hstack( (self.vertices, onecolumn ) )
        # transform all vertices 2 voxel index space
        # affint.T so that each column is a vertex, then matrix mul will multiply all
        findices = self.invaffine.dot(affine_vertices.T).T
        # to index we need ints and cut the homog coord
        return findices.round().astype(int)[:,:-1]

    def voxels2dots(self):
        ''' transforms voxels coords according to affine and ret a sot seq
            returns pointxyz, voxelvalue
            iteration order is z first then y finally x
        '''
        nx, ny, nz = self.voxels.shape
        # is there a simple way to vectorize this?
        # besides constructing a k, j, i matrix ?

        # some optimizations
        affine = self.affine
        voxels = self.voxels
        dots = [0]*nx*ny*nz*3
        vals = [0]*nx*ny*nz
        idx = 0

        for i in xrange(nx):
            for j in xrange(ny):
                for k in xrange(nz):
                    vox = voxels[i,j,k]
                    if vox :
                        vals[idx] = vox
                        tr = np.round(affine.dot([i,j,k,1]))
                        dots[3*idx] = tr[0]
                        dots[3*idx+1] = tr[1]
                        dots[3*idx+2] = tr[2]
                        idx += 1

        return dots, vals


    def mapping(self):
        'vertex 2 voxel value'
        indices = self.vertices2voxel_indices()
        vertex_voxel_values = []

        for idx in indices:
            v = self.voxels[tuple(idx)]
            vertex_voxel_values.append(v)

        return vertex_voxel_values

    def evaluate_mapping_correctness(self):
        region_map = self.mapping()
        c = Counter(region_map)
        print 'total vertices       : %s' % len(self.vertices)
        print 'vertices mapped to 0 : %s' % c[0]


VOXELS_PTH='data/rm+thal&bg_1mm_20111013_uint8.nii'
VERTICES_PTH='data/vertices.txt'

def load_nii(pth):
    img = nibabel.load(pth)
    h = img.get_header()
    voxels = img.get_data()
    affine = h.get_base_affine()
    return voxels, affine

def load_vertices(pth):
    with open(pth) as f:
        return np.loadtxt(f)

def main_vox2pnt():
    voxels, affine = load_nii(VOXELS_PTH)
    m = Mapper(voxels, None, affine)
    dots, vox = m.voxels2dots()
    np.savetxt('data/nii_points', dots, fmt='%d', delimiter=',',
        newline=',')
    np.savetxt('data/nii_vox', vox, fmt='%.1e', delimiter=',',
        newline=',')

if __name__ == '__main__':
    try:
        main_vox2pnt()
    except Exception, e:
        print e
