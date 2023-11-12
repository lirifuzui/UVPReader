import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from pyuvp import ForMetflowUvp

files = [70, 75, 80, 85, 90]
diff_P = np.array([-259.6438709, -248.9572471, -239.7117803, -231.2320523, -220.1030211]) + 302.8222761

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
    coords_origin = coords_origin - 26
    coords = coords_origin[30:120]
    vel = np.mean(vel, axis=0)
    vel = vel[30:120]
    params, covariance = curve_fit(velosity_perfile, coords / 1000, vel / 1000, p0=0.5)
    plt.scatter(coords / 1000, vel / 1000)
    plt.plot(coords / 1000, velosity_perfile(coords / 1000, params[0]))
    print(params[0])
plt.grid()
plt.show()
