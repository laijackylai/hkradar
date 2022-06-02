from datetime import datetime
import Nio
import numpy as np
import os
import multiprocessing
from multiprocessing import Pool
# import json
# import compress_json
# import msgpack
# import gzip
# import radar_pb2 # * tested proto but failed due to my incompetence
from plyfile import PlyData, PlyElement

TEST_DIR = './test/'
HAIL_DIR = './20210916/'
NORMAL_DIR = './20220322/'


def process(file):
    """
    process nc
    """

    name = file.split('/')[3].split('.')[0]

    f64 = TEST_DIR + '64.nc'
    f256 = TEST_DIR + '256.nc'

    grid64 = np.genfromtxt('./TMS_064grid.csv', delimiter=',')
    lon = grid64[0:480][:]
    lat = grid64[480:960][:]
    # grid256 = './TMS_256grid.csv'

    f = Nio.open_file(file, 'r')
    # vars = list(f.variables.keys())
    # * ['time', 'height', 'y', 'x', '__xarray_dataarray_variable__']

    time = f.variables['time']
    time_data = np.array(time[:])
    time_dict = time.__dict__
    # * time string in format of "x days since `date` `time`"
    time = str(time_data[0]) + ' ' + time_dict['units']

    height = f.variables['height']
    height_data = np.array(height[:])

    d = f.variables['__xarray_dataarray_variable__']
    data = np.array(d[:])  # * shape (1, 31, 480, 480)
    d_dict = d.__dict__

    ply_data = []
    # coord_data = []
    # reflectivity_data = []
    # color_data = []

    for z in range(31):
        height = height_data[z]
        single_layer = data[0][z][:][:]
        i, j = single_layer.shape
        for x in range(i):
            for y in range(j):
                longitude = lon[x][y]
                latitude = lat[x][y]
                dBZ = single_layer[x][y]
                # obj = {
                #     'position': [longitude, latitude, height],
                #     'reflectivity': dBZ,
                #     'color': getColor(dBZ)
                # }
                # pbf.append(obj)

                # * write ply
                # coordinates = (longitude, latitude, height)
                # coord_data.append(coordinates)

                # reflectivity = dBZ
                # reflectivity_data.append(reflectivity)

                # color = getColor(dBZ)
                # color_data.append(tuple(color))

                if dBZ > 0:
                    color = getColor(dBZ)
                    single_entry = (longitude, latitude, height,
                                    *tuple(color), dBZ, dBZ)
                    ply_data.append(single_entry)

                # * test proto
                # pos = radar_pb2.Position()
                # pos.longitude = longitude
                # pos.latitude = latitude
                # pos.height = height

    ply_data = np.array(ply_data, dtype=[
        ('x', 'f4'),
        ('y', 'f4'),
        ('z', 'f4'),
        ('red', np.uint8),
        ('green', np.uint8),
        ('blue', np.uint8),
        ('s', 'f4'),
        ('t', 'f4'),
    ])

    # * structure the data
    # coord_data = np.array(
    #     coord_data, dtype=[('lon', 'f4'), ('lat', 'f4'), ('height', 'f4')])
    # reflectivity_data = np.array(reflectivity_data, dtype=[('dBZ', 'f4')])
    # color_data = np.array(
    #     color_data, dtype=[('r', 'u1'), ('g', 'u1'), ('b', 'u1')])

    el = PlyElement.describe(ply_data, 'vertex', comments=[
        'contains radar CAPPI data', 'format in ((lon, lat, height), (r, g, b), (dBZ, dBZ))'])
    PlyData([el]).write(NORMAL_DIR + name + '.ply')
    PlyData([el], text=True).write(NORMAL_DIR + name + '_ascii' + '.ply')
    print(name)

    # * save ply
    # coord_el = PlyElement.describe(coord_data, 'coordinates', comments=[
    #                                'coordinates of point clouds'])
    # reflectivity_el = PlyElement.describe(
    #     reflectivity_data, 'dBZ', comments=['reflectivity'])
    # color_el = PlyElement.describe(color_data, 'color', comments=[
    #                                'color of point clouds'])
    # PlyData([coord_el, reflectivity_el, color_el]).write(TEST_DIR + 'data.ply')
    # PlyData([coord_el, reflectivity_el, color_el],
    #         text=True).write(TEST_DIR + 'data_ascii.ply')

    # * test msgpack
    # with gzip.open(TEST_DIR + 'test.msgpack.gz', 'wb') as outfile:
    #     packed = msgpack.packb(write_data)
    #     outfile.write(packed)

    # * test compress_json library
    # compress_json.dump(write_data, TEST_DIR + 'test.json.gz')
    # compress_json.dump(write_data, TEST_DIR + 'test.json.bz')
    # compress_json.dump(write_data, TEST_DIR + 'test.json.lzma')

    # with open(TEST_DIR + 'test.json', 'w') as test:
    #     test.write(write_string)


def getColor(dBZ):
    """color code referencing https://www.weather.gov/jetstream/refl#:~:text=The%20color%20scale%20is%20located,cm

    Args:
        dBZ (int): reflectivity

    Returns:
        array: color
    """
    if(dBZ < -30):
        return [211, 253, 253]
    if(dBZ < -25):
        return [199, 155, 203]
    if(dBZ < -20):
        return [141, 98, 146]
    if(dBZ < -15):
        return [97, 53, 100]
    if(dBZ < -10):
        return [206, 205, 152]
    if(dBZ < -5):
        return [152, 154, 102]
    if(dBZ < 0):
        return [98, 98, 97]
    if(dBZ < 5):
        return [108, 231, 231]
    if(dBZ < 10):
        return [69, 155, 238]
    if(dBZ < 15):
        return [2, 0, 232]
    if(dBZ < 20):
        return [117, 250, 76]
    if(dBZ < 25):
        return [89, 193, 56]
    if(dBZ < 30):
        return [60, 136, 38]
    if(dBZ < 35):
        return [253, 249, 83]
    if(dBZ < 40):
        return [228, 190, 64]
    if(dBZ < 45):
        return [239, 155, 56]
    if(dBZ < 50):
        return [229, 50, 35]
    if(dBZ < 55):
        return [191, 40, 28]
    if(dBZ < 60):
        return [163, 33, 25]
    if(dBZ < 65):
        return [226, 49, 244]
    if(dBZ < 70):
        return [139, 89, 186]
    if(dBZ < 75):
        return [254, 254, 254]


if __name__ == '__main__':
    start = datetime.now()
    list = []
    for subdir, dirs, files in os.walk(NORMAL_DIR):
        for file in files:
            # print os.path.join(subdir, file)
            filepath = subdir + os.sep + file

            if filepath.endswith(".nc"):
                list.append(filepath)

    with Pool(multiprocessing.cpu_count()) as p:
        p.map(process, list)

    end = datetime.now()
    print('time used: ', start - end)
