import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

from pyuvp import ForMetflowUvp

files = [70, 75, 80, 85, 90]
diff_P = np.array([-264.9300263, -252.3871998, -250.2671287, -241.0135767, -232.8278945]) + 303.2681338
result = []
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
    coords = coords_origin[30:150]
    subarrays = np.vsplit(vel, 20)
    for subarr in subarrays:
        subarr = np.mean(subarr, axis=0)
        subarr = subarr[30:150]
        params, covariance = curve_fit(velosity_perfile, coords / 1000, subarr / 1000, p0=0.5)
        plt.scatter(coords / 1000, subarr / 1000)
        plt.plot(coords / 1000, velosity_perfile(coords / 1000, params[0]))
        print(params[0])
        result.append(params[0])

    print('=================')
result = np.array(result)
np.savetxt('result.csv', result, delimiter=',')
plt.grid()
plt.show()
