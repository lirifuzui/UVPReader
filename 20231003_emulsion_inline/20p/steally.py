import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from pyuvp import ForMetflowUvp
'''
files = [55, 60, 65, 70, 75, 80]
diff_P = np.array([-221.8528493, -214.6389876, -207.0681031, -193.2732707, -188.6253676, -178.3344718]) + 235.8406247'''

files =  [65, 70]
diff_P = np.array([ -207.0681031, -193.2732707]) + 235.8406247

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
    coords_origin = coords_origin - 27
    coords = coords_origin[15:60]
    vel = np.mean(vel, axis=0)
    vel = vel[15:60]
    params, covariance = curve_fit(velosity_perfile, coords / 1000, vel / 1000, p0=0.5)
    plt.scatter(coords / 1000, vel / 1000)
    plt.plot(coords / 1000, velosity_perfile(coords / 1000, params[0]))
    print(params[0])
plt.xlim(-0.020, 0)
plt.show()
