from plyfile import PlyData, PlyElement
import numpy as np

TEST_DIR = './test/'

def main():
    # read()
    write()
    
def write():
    # * write data to ply file
    # * data structure (coordinates: lon, lat, height), (reflectivity: dBZ), (color: r, g, b)
    data = np.array(
        [
            ([0, 0, 0], 10, [0, 0, 0]), # * format in ([lon, lat, height], dBZ, (r, g, b))
            ([0, 0, 1], 20, [0, 0, 255]),
            ([0, 1, 0], 30, [0, 255, 0]),
            ([0, 1, 1], 40, [0, 255, 255]),
            ([1, 0, 0], 50, [255, 0, 0])
        ],
        dtype=[
            ('coordinates', 'f4', (3,)),
            ('reflectivity', 'f4'),
            ('color', 'u1', (3,))
        ]
    )
    el = PlyElement.describe(data, 'data', comments=[
                             'contains radar CAPPI data', 'format in ([lon, lat, height], dBZ, (r, g, b))'])
    PlyData([el]).write('data.ply')
    PlyData([el], text=True).write('data_ascii.ply')
    print('done')

def read():
    # * reading test ply file
    with open(TEST_DIR + 'tet.ply', 'rb') as f:
        plydata = PlyData.read(f)
        print(plydata.elements[0].data)

if __name__ == '__main__':
    main()
    