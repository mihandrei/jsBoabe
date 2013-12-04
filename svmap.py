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


def load_region_id_to_index_map(pth):
    region_id_to_region_idx = {}
    with open(pth) as f:
        for idx, line in enumerate(f):
            rid, name = line.split()
            region_id_to_region_idx[int(rid)] = idx
    return region_id_to_region_idx


def load_region_centers(pth):
    ret = []
    with open(pth) as f:
        next(f)
        for idx, line in enumerate(f):
            name, x, y, z = line.split()
            ret.append((float(x), float(y), float(z)))
    return ret


def _cube_neighborhood(radius=2):
    d = []
    r = range(-radius, radius+1)
    for i in r:
        for j in r:
            for k in r:
                d.append((i, j, k))
    return d


class Mapper(object):
    def __init__(self, voxels, vertices, affine, region_id_to_region_idx, centers):
        self.voxels = voxels
        self.vertices = vertices
        self.affine = affine
        self.invaffine = np.linalg.inv(self.affine)
        self.region_id_to_region_idx = region_id_to_region_idx
        self.region_idx_to_region_id = dict((v, k) for k, v in region_id_to_region_idx.iteritems())
        self.centers = centers

    def stats(self):
        print 'voxels'
        counts = Counter(self.voxels.flat)
        print 'unique values %s' % len(counts)

        for kv in counts.iteritems():
            print '%s : %s' % kv

        print 'voxel positions after affine transform'
        print '000 - %s' % self.affine.dot([0, 0, 0, 1])
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
        # to index we need ints
        int_indices = np.round(findices).astype(int)
        #and cut the homog coord
        return int_indices[:, :-1]

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

    _neigh2 = _cube_neighborhood(radius=2)
    _neigh4 = _cube_neighborhood(radius=4)
    _neigh8 = _cube_neighborhood(radius=8)
    _neigh12 = _cube_neighborhood(radius=12)

    def _sample_neighbourhood(self, i, j, k):
        def _sample(neigh):
            vals = []

            for di, dj, dk in neigh:
                v = self.voxels[i + di, j + dj, k + dk]
                if v != 0:
                    vals.append(v)

            if vals:
                return Counter(vals).most_common()[0][0]
            else:
                return 0

        v = _sample(self._neigh2)
        if v:
            return v
        v = _sample(self._neigh4)
        if v:
            return v
        v = _sample(self._neigh8)
        if v:
            return v
        v = _sample(self._neigh12)
        if v:
            return v
        return 0

    def _sample_distance2centers(self, vertex):
        vx, vy, vz = vertex

        def dist(c):
            cx, cy, cz = c[1]
            return (cx - vx)**2 + (cy - vy)**2 + (cz - vz)**2

        closest_center = max(enumerate(self.centers), key=dist)
        return self.region_idx_to_region_id[closest_center[0]]

    def mapping(self):
        """vertex 2 voxel value"""
        voxel_indices = self.vertices2voxel_indices()
        vertex_voxel_values = []

        for vertex_id, voxel_idx in enumerate(voxel_indices):
            i, j, k = tuple(voxel_idx)
            v = self.voxels[i, j, k]
            if v == 0:
                v = self._sample_neighbourhood(i, j, k)
                #v = self._sample_distance2centers(self.vertices[vertex_id])
            vertex_voxel_values.append(v)

        return vertex_voxel_values

    def mapping2regionmap(self):
        mapping = self.mapping()
        id_to_index = self.region_id_to_region_idx
        ret = []
        for v in mapping:
            if v != 0:
                ret.append(id_to_index[v] + 1)
            else:
                #FIXME: this is a baaaad default, temporary workaround to see data intvb
                ret.append(0)
        return ret

    def evaluate_mapping_correctness(self):
        region_map = self.mapping()
        c = Counter(region_map)
        mapped2zero = c[0]
        mapped_ok = len(self.vertices) - mapped2zero
        ok_avg = mapped_ok / (len(c) - 1)
        print 'total vertices                 : %s' % len(self.vertices)
        print 'vertices mapped to zero region : %s' % mapped2zero
        print 'average number of vertices '
        print '    per non-zero region        : %s ' % ok_avg
        
        if mapped2zero > 0.10 * ok_avg:
            print 'this looks bad:\n bads are more than 10% of goods'
        print c

        # print non-mapped vertices
        #for i in xrange(len(region_map)):
        #    if region_map[i] == 0:
        #        print "%s " % self.vertices[i]
