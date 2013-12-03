"""
This script maps each vertex of a surface to a region.

voxels
    Volumetric data mapping a voxel to a region code.
vertices
    Vertices assumed to be from a surface that is compatible with the
    volume described by voxels
"""
import numpy as np
import nibabel
from collections import Counter
import matplotlib.pyplot as plt


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

        for kv in counts.iteritems():
            print '%s : %s' % kv

        print 'voxel positions after affine transform'
        print '000 - %s' % self.affine.dot([0,0,0,1])
        print '111 - %s' % self.affine.dot(list(self.voxels.shape) + [1])

        print 'vertices positions'
        print 'x y z mins %s' % np.min(self.vertices, axis=0)
        print 'x y z maxs %s' % np.max(self.vertices, axis=0)

    def bbox_surface(self):
        minx = miny = minz = 1e10
        maxx = maxy = maxz = -1e10
        for x, y, z in self.vertices:
            minx = min(minx, x)
            maxx = max(maxx, x)
            miny = min(miny, y)
            maxy = max(maxy, y)
            minz = min(minz, z)
            maxz = max(maxz, z)            
        return minx, miny, minz, maxx, maxy, maxz

    def bbox_voxels(self):
        """trim 0 planes in index space
        this is less relevant if the affine has a non 90 rotation
        but that is uncommon and this case is easy to implement
        """
        dx, dy, dz = self.voxels.shape
        imin = imax = jmin = jmax = kmin = kmax = None

        for i in xrange(dz):
            if np.count_nonzero(self.voxels[:, :, i]) != 0:
                kmin = i
                break
        for i in xrange(dz):                
            if np.count_nonzero(self.voxels[:, i, :]) != 0:
                jmin = i
                break
        for i in xrange(dz):        
            if np.count_nonzero(self.voxels[i, :, :]) != 0:
                imin = i
                break
        for i in xrange(dz):        
            if np.count_nonzero(self.voxels[:, :, -i-1]) != 0:
                kmax = dz - i - 1
                break
        for i in xrange(dz):        
            if np.count_nonzero(self.voxels[:, -i-1, :]) != 0:
                jmax = dy - i - 1
                break
        for i in xrange(dz):        
            if np.count_nonzero(self.voxels[-i-1, :, :]) != 0:
                imax = dx - i - 1
                break
        return imin, jmin, kmin, imax, jmax, kmax

    def vertices2voxel_indices(self):
        onecolumn = np.ones((self.vertices.shape[0], 1))
        # we add a homogen coord 2 all vertices
        affine_vertices = np.hstack((self.vertices, onecolumn))
        # transform all vertices 2 voxel index space
        # affint.T so that each column is a vertex, then matrix mul will multiply all
        findices = self.invaffine.dot(affine_vertices.T).T
        # to index we need ints and cut the homog coord
        return findices.round().astype(int)[:, :-1]

    def voxels2vertices(self):
        """ transforms voxels coords according to affine and ret a seq
            returns pointxyz, voxelvalue
            iteration order is z first then y finally x
        """
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
                    vox = voxels[i, j, k]
                    if vox:
                        vals[idx] = vox
                        tr = affine.dot([i, j, k, 1])
                        dots[3*idx] = tr[0]
                        dots[3*idx+1] = tr[1]
                        dots[3*idx+2] = tr[2]
                        idx += 1

        return dots[:3*idx], vals[:idx]

    def mapping(self):
        """vertex 2 voxel value"""
        indices = self.vertices2voxel_indices()
        vertex_voxel_values = []

        for idx in indices:
            v = self.voxels[tuple(idx)]
            vertex_voxel_values.append(v)

        return vertex_voxel_values

    def evaluate_mapping_correctness(self):
        region_map = self.mapping()
        c = Counter(region_map)
        mapped2zero = c[0]
        mappedOk = len(self.vertices) - mapped2zero
        okAvg = mappedOk / (len(c) - 1)
        print 'total vertices                 : %s' % len(self.vertices)
        print 'vertices mapped to zero region : %s' % mapped2zero
        print 'average number of vertices '
        print '    per non-zero region        : %s ' % okAvg
        
        if mapped2zero > 0.10 * okAvg:
            print 'this looks bad:\n bads are more than 10% of goods'
        print c

        # print non-mapped vertices
        #for i in xrange(len(region_map)):
        #    if region_map[i] == 0:
        #        print "%s " % self.vertices[i]

    def view_section(self):
        plt.figure()
        plt.title('self.voxels[:, :, 100]')
        plt.imshow(self.voxels[:, :, 100], origin="lower")
        plt.figure()
        plt.title('self.voxels[:, 100, :]')
        plt.imshow(self.voxels[:, 100, :], origin="lower")
        plt.figure()
        plt.title('self.voxels[100, :, :]')
        plt.imshow(self.voxels[100, :, :], origin="lower")
        plt.show()


VOXELS_PTH = 'data/rm+thal&bg_1mm_20111013_uint8.nii'
VERTICES_PTH = 'data/vertices.txt'


def load_nii(pth):
    img = nibabel.load(pth)
    h = img.get_header()
    voxels = img.get_data()
    # affine = h.get_base_affine()
    affine = h.get_best_affine()
    # ajust the affine
    sx = sy = sz = 1
    ajusting = np.array(
        [[sx,  0.0,  0.0,   0.0],
         [0.0,  sy,  0.0,   0.0],
         [0.0,  0.0,  sz,   0.0],
         [0.0,  0.0,  0.0,  1.0]])

    affine = ajusting.dot(affine)

    return voxels, affine


def load_vertices(pth):
    with open(pth) as f:
        return np.loadtxt(f)


def main_save_voxel_vertices():
    voxels, affine = load_nii(VOXELS_PTH)
    m = Mapper(voxels, None, affine)
    dots, vox = m.voxels2vertices()

    with open('data/nii_points.txt', 'w') as f:
        for i in xrange(0, len(dots), 3):
            f.write(' '.join(str(v) for v in dots[i: i+3]))
            f.write('\n')

    with open('data/nii_voxels.txt', 'w') as f:
        for v in vox:
            f.write(str(v))
            f.write('\n')

def main_bboxes():
    voxels, affine = load_nii(VOXELS_PTH)
    vertices = load_vertices(VERTICES_PTH)
    m = Mapper(voxels, vertices, affine)
    print 'surface bbox min xyz max xyz'
    print ['%.1f' % q for q in m.bbox_surface()]
    print 'voxel trimmed !=0 planes. Plane indices min max ijk'
    imin, jmin, kmin, imax, jmax, kmax = m.bbox_voxels()
    print imin, jmin, kmin, imax, jmax, kmax
    print 'these through the affine'
    print 'min %s' % m.affine.dot([imin, jmin, kmin, 1])
    print 'max %s' % m.affine.dot([imax, jmax, kmax, 1])
    print voxels.shape
    print m.affine
    m.view_section()


def main_eval_mapping():
    voxels, affine = load_nii(VOXELS_PTH)
    vertices = load_vertices(VERTICES_PTH)
    m = Mapper(voxels, vertices, affine)
    m.evaluate_mapping_correctness()

def main_stats():
    voxels, affine = load_nii(VOXELS_PTH)
    vertices = load_vertices(VERTICES_PTH)
    m = Mapper(voxels, vertices, affine)
    print m.vertices.shape
    print m.voxels.shape
    print np.count_nonzero(m.voxels)
    print m.stats()

import traceback

if __name__ == '__main__':
    try:
        # main_bboxes()
        main_eval_mapping()
        #main_save_voxel_vertices()
        #main_stats()
    except Exception, e:
        traceback.print_exc()
