"""
This script maps each vertex of a surface to a region.
"""
from svmap import load_nii, load_region_id_to_index_map, load_region_centers, load_vertices
from svmap import Mapper

VOXELS_PTH = '/home/mihai.andrei/workspace/tvb/demo_data/regionMapping/rm+thal&bg_1mm_20111013_uint8.nii'
VERTICES_PTH = '/home/mihai.andrei/workspace/tvb/demo_data/regionMapping/surface_80k_vertices.txt'
REGION_ID2IDX_PTH = '/home/mihai.andrei/workspace/tvb/demo_data/connectivity/dti_pipeline_regions.txt'
REGION_CENTERS = '/home/mihai.andrei/workspace/tvb/demo_data/connectivity/connectivity_regions_96/positions.txt'


def view_sections(voxels, x, y, z):
    import matplotlib.pyplot as plt

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


def _write_file(pth, seq, sep=' '):
    with open(pth, 'w') as f:
        for v in seq:
            f.write('{0}{1}'.format(v, sep))


def main_save_data_for_viewer():
    """to be viewed by webgl"""
    m = make_mapper()
    raw_mapping = m.mapping()
    dots, vox = m.voxels2vertices()

    with open('viewerdata/nii_points.txt', 'w') as f:
        for i in xrange(0, len(dots), 3):
            f.write(' '.join(str(v) for v in dots[i: i+3]))
            f.write('\n')

    _write_file('viewerdata/nii_raw_voxels.txt', vox, sep='\n')
    _write_file('viewerdata/nii_raw_mapping_distc.txt', raw_mapping)


def main_write_regionmap(pth):
    m = make_mapper()
    raw_mapping = m.mapping()
    m.evaluate_mapping_correctness(raw_mapping)
    _write_file(pth, m.mapping2regionmap(raw_mapping))


def main_write_heuristic_map(pth):
    m = make_mapper()
    raw_mapping = m.heuristic_mapping()
    m.evaluate_mapping_correctness(raw_mapping)
    _write_file(pth, m.mapping2regionmap(raw_mapping))


def main_stats():
    m = make_mapper()
    m.stats()

if __name__ == '__main__':
    #main_stats()
    main_write_regionmap('96connectivity_to_srf_80k_map.txt')
    #main_write_heuristic_map('96connectivity_to_srf_80k_heuristic_map.txt')