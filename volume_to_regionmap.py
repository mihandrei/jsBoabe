"""
This script maps each vertex of a surface to a region.

voxels
    Volumetric data mapping a voxel to a region code.
vertices
    Vertices assumed to be from a surface that is compatible with the
    volume described by voxels
"""
import numpy as np
import matplotlib.pyplot as plt
from svmap import load_nii, load_region_id_to_index_map, load_region_centers, load_vertices, Mapper

VOXELS_PTH = 'data/rm+thal&bg_1mm_20111013_uint8.nii'
VERTICES_PTH = 'data/vertices.txt'
REGION_ID2IDX_PTH = '/home/mihai.andrei/workspace/tvb/demo_data/connectivity/dti_pipeline_regions.txt'
REGION_CENTERS = '/home/mihai.andrei/workspace/tvb/demo_data/connectivity/sdasdas/positions.txt'


def view_sections(voxels, x, y, z):
    plt.figure()
    plt.title('voxels[:, :, %d]' % z)
    plt.imshow(voxels[:, :, z], origin="lower")
    plt.figure()
    plt.title('voxels[:, %d, :]' % y)
    plt.imshow(voxels[:, y, :], origin="lower")
    plt.figure()
    plt.title('voxels[%d, :, :]' % x)
    plt.imshow(voxels[x, :, :], origin="lower")
    plt.show()


def make_mapper():
    voxels, affine = load_nii(VOXELS_PTH)
    vertices = load_vertices(VERTICES_PTH)
    region_id_to_idx = load_region_id_to_index_map(REGION_ID2IDX_PTH)
    centers = load_region_centers(REGION_CENTERS)

    return Mapper(voxels, vertices, affine, region_id_to_idx, centers)


def main_save_voxel_vertices():
    """saves voxels as vertices so that they can be viewed by webgl"""
    m = make_mapper()
    dots, vox = m.voxels2vertices()

    with open('data/nii_points.txt', 'w') as f:
        for i in xrange(0, len(dots), 3):
            f.write(' '.join(str(v) for v in dots[i: i+3]))
            f.write('\n')

    with open('data/nii_raw_voxels.txt', 'w') as f:
        for v in vox:
            f.write(str(v))
            f.write('\n')


def main_write_regionmap():
    m = make_mapper()
    m.evaluate_mapping_correctness()

    with open('data/nii_raw_mapping_neigh.txt', 'w') as f:
        for v in m.mapping():
            f.write('%s ' % v)

    with open('data/nii_mapping_neigh.txt', 'w') as f:
        for v in m.mapping2regionmap():
            f.write('%s ' % v)


def main_bboxes():
    m = make_mapper()
    print 'surface bbox min xyz max xyz'
    print ['%.1f' % q for q in m.bbox_surface()]
    print 'voxel trimmed !=0 planes. Plane indices min max ijk'
    imin, jmin, kmin, imax, jmax, kmax = m.bbox_voxels()
    print imin, jmin, kmin, imax, jmax, kmax
    print 'these through the affine'
    print 'min %s' % m.affine.dot([imin, jmin, kmin, 1])
    print 'max %s' % m.affine.dot([imax, jmax, kmax, 1])
    print m.voxels.shape
    print m.affine
    view_sections(m.voxels, 100,100,100)


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
        #main_bboxes()
        main_write_regionmap()
        #main_save_voxel_vertices()
        #main_stats()
    except Exception, e:
        traceback.print_exc()
