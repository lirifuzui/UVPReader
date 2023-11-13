import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from pyuvp import ForMetflowUvp

files = [85, 90]
makers = ['*', '+']
diff_P = np.array([-231.2320523, -220.1030211]) + 302.8222761
plt.figure(figsize=(5, 5))
plt.rcParams['axes.linewidth'] = 2
plt.tick_params(axis='both', which='both', width=1.5, length=6)
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
    coords_origin = coords_origin - 26.3
    coords = coords_origin[48:100]
    vel = np.mean(vel, axis=0)
    vel = vel[48:100]
    vel = vel[::2]
    coords = coords[::2]
    params, covariance = curve_fit(velosity_perfile, coords / 1000, vel / 1000, p0=0.5)
    x = np.linspace(-0.025, 0.025, 200)
    plt.plot(x, velosity_perfile(x, params[0]), color = 'red')
    plt.scatter(coords / 1000, vel / 1000, color = "black",marker= makers[n], label = '1')
    print(params[0])
plt.xlim(-0.020, 0)
plt.ylim(0,0.2)
plt.legend()
plt.show()

