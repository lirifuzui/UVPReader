import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from pyuvp import ForMetflowUvp

from pyuvp import ForMetflowUvp

files = [60, 65, 70, 75, 80]
diff_P = np.array([-220.6969055, -212.3003921, -206.2043178, -199.6272439, -193.4427466]) + 234.9178592
result = []
for n, file in enumerate(files):
    # 定义拟合函数
    delta_P = diff_P[n] * 10
    Rudio = 0.025
    L = 0.46


    def velosity_perfile(r, miu):
        return delta_P / (4 * miu * L) * (Rudio ** 2 - (r) ** 2)


    # 文件数据
    data = ForMetflowUvp.readFile(str(file) + ".mfprof")
    data._data_show(1010)
    vel = data.velTables[0] * 2
    coords_origin = data.coordinateArrays[0] * np.cos(30 / 180 * np.pi)
    coords_origin = coords_origin - 29
    coords = coords_origin[15:60]
    subarrays = np.vsplit(vel, 20)
    for subarr in subarrays:
        subarr = np.mean(subarr, axis=0)
        subarr = subarr[15:60]
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
