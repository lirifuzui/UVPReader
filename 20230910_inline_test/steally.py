import matplotlib.pyplot as plt
import numpy as np
import csv

from pyuvp import uvp

emulsion_name = 'emulsion30'

files = ["_duty60", "_duty65", "_duty70", "_duty75", "_duty80"]

for file in files:
    data = uvp.readUvpFile(emulsion_name + file + ".mfprof")
    # data.redefineSoundSpeed(1029)
    vel_origin = data.velTables[0]
    coords_origin = data.coordinateArrays[0] * np.cos(30 / 180 * np.pi)
    vel_ave = np.mean(vel_origin, axis=0)
    csv_file = emulsion_name + file + '.csv'
    combined_array = np.column_stack((coords_origin, vel_ave))

    # 使用CSV模块将二维数组写入CSV文件
    with open(csv_file, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        # 写入标题行（可选）
        writer.writerow(['coords', 'vel_ave'])
        # 写入数据行
        writer.writerows(combined_array)


