import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

from pyuvp import uvp

files = np.array([65, 70, 72])
press_diff = 151.98 * files - 7407.7 - (151 * files - 2203.7) + 5145.618068

plt.figure()


# 定义拟合函数
def linear_function(x, m, b):
    return m * x + b


for n, file in enumerate(files):
    data = uvp.readUvpFile(str(file) + ".mfprof")
    # data.redefineSoundSpeed(1029)
    vel = data.velTables[0] * 2
    coords_origin = data.coordinateArrays[0] * np.cos(30 / 180 * np.pi)
    coords = []
    for i in range(len(coords_origin)):
        coords.append(np.abs(coords_origin[i] - (10.26 + 25)))

    coords = np.array(coords[21:33])
    vel = vel[:, 21:33]
    vel = np.mean(vel, axis=0)
    du_dr = np.abs(np.gradient(vel, coords))
    alpha = float(press_diff[n] / 0.46)
    visc = alpha * coords / (2 * du_dr)

    plt.scatter(du_dr, visc)
plt.show()
