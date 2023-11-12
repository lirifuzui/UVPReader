import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from pyuvp import ForMetflowUvp

files = [55, 60, 65, 70, 75, 80]
diff_P = np.array([-224.2428355, -212.9580568, -206.6233397, -197.8812467, -193.3746336, -186.7326596]) + 235.563764

for n, file in enumerate(files):
    # 定义拟合函数
    delta_P = diff_P[n] * 10
    Rudio = 0.025
    L = 0.46


    def velosity_perfile(r, miu):
        return delta_P / (4 * miu * L) * (Rudio ** 2 - (r) ** 2)


    # 文件数据
    data = ForMetflowUvp.readUvpFile(str(file) + ".mfprof")
    data.defineSoundSpeed(1010)
    vel = data.velTables[0] * 2
    coords_origin = data.coordinateArrays[0] * np.cos(30 / 180 * np.pi)
    coords_origin = coords_origin - 29
    coords = coords_origin[15:60]
    vel = np.mean(vel, axis=0)
    vel = vel[15:60]
    params, covariance = curve_fit(velosity_perfile, coords / 1000, vel / 1000, p0=0.5)
    plt.scatter(coords / 1000, vel / 1000)
    plt.plot(coords / 1000, velosity_perfile(coords / 1000, params[0]))
    print(params[0])
plt.grid()
plt.show()
