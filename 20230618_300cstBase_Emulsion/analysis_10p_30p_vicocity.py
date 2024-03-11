import matplotlib.pyplot as plt
import numpy as np
from pyuvp import ForMetflowUvp
File = [
    ["10p_05hz150deg.mfprof", "10p_1hz60deg.mfprof", "10p_1hz90deg.mfprof", ],
    ["15p_05hz90deg.mfprof", "15p_05hz120deg.mfprof", "15p_1hz60deg_2.mfprof", ],
    ["20p_1hz60deg.mfprof","20p_05hz120deg.mfprof","20p_05hz90deg.mfprof",],
    ["25p_05hz90deg.mfprof", "25p_05hz120deg.mfprof","25p_1hz90deg.mfprof",],
    ["30p_1hz60deg.mfprof","30p_05hz90deg.mfprof","30p_05hz150deg.mfprof",],
    ["35p_1hz90deg.mfprof","35p_1hz120deg.mfprof","35p_1hz60deg.mfprof"]
]

plt.figure(figsize=(6.6, 6))
# 设置坐标轴刻度线条粗度
plt.rcParams['axes.linewidth'] = 3
plt.tick_params(axis='both', direction='in',which='both', width=1.5, length=6)
plt.xlim(0.05, 0.40)
plt.xlabel(r'x')
plt.ylabel(r'y')
result = []
for files in File:
    Visc = []
    Shear_rate = []
    Coord = []
    for file in files:
        data = ForMetflowUvp.readFile(file)
        # data.redefineSoundSpeed(1029)
        vel_origin = data.velTables[0]
        coords_origin = data.coordinateArrays[0]
        analysis = data.createUSRAnalysis()
        analysis.channelRange(80, 90)
        analysis.cylinderGeom(77, 106.77, 10.62)
        analysis.slicing(5)
        visc, shearrate = analysis.rheologyViscosity(smooth_level=9, ignoreException=True)
        Visc.extend(list(visc))
    result.append(Visc)

result = np.array(result) / 300
result = result.T

positions = [0.10, 0.15, 0.20, 0.25,  0.30, 0.35]

plt.boxplot(result, 1, positions=positions, widths=0.008, showfliers=False)



K = 1 / 300
y_r = np.array([i / 20 for i in range(24, 70)])
y = y_r*((2*y_r + 5*K)/(2+5*K))**(3/2)
phi_m = 0.48
phi = phi_m / (9 / (8 * y) + 1) ** 3
plt.plot(phi, y_r, label='Frankel and Acrivos', color = "red")
y_r = np.array([i / 20 for i in range(20, 32)])
y = y_r*((2*y_r + 5*K)/(2+5*K))**(3/2)
phi = phi_m / (9 / (8 * y) + 1) ** 3
plt.plot(phi, y_r, label='Frankel and Acrivos', color = "red",linestyle='--')

plt.show()