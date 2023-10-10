import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

from pyuvp import uvp

files = [55, 60, 65, 70, 75, 80]
diff_P = np.array([-301.0619661, -295.7176311, -288.8381609, -284.0474192, -276.7541743, -268.7440538]) + 307.0992712
for n, file in enumerate(files):
    # 定义拟合函数
    delta_P = diff_P[n] * 10
    Rudio = 0.025
    L = 0.46


    def velosity_perfile(r, miu):
        return delta_P / (4 * miu * L) * (Rudio ** 2 - (r) ** 2)


    # 文件数据
    data = uvp.readUvpFile(str(file) + ".mfprof")
    data.defineSoundSpeed(1010)
    vel = data.velTables[0] * 2
    coords_origin = data.coordinateArrays[0] * np.cos(30 / 180 * np.pi)
    coords_origin = coords_origin - 27
    coords = coords_origin[21:40]
    vel = np.mean(vel, axis=0)
    vel = vel[21:40]
    params, covariance = curve_fit(velosity_perfile, coords / 1000, vel / 1000, p0=0.5)
    plt.figure()
    plt.scatter(coords / 1000, vel / 1000)
    plt.plot(coords / 1000, velosity_perfile(coords / 1000, params[0]))
    plt.show()
    print(params[0])
