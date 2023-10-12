import matplotlib.pyplot as plt
import numpy as np
import csv
from pyuvp import uvp

# files = ["10p_05hz90deg.mfprof", "10p_05hz120deg_2.mfprof", "10p_05hz150deg.mfprof", "10p_1hz60deg.mfprof", "10p_1hz90deg.mfprof", "10p_1hz120deg.mfprof"]
# files = ["15p_05hz90deg.mfprof","15p_05hz120deg.mfprof","15p_05hz150deg.mfprof","15p_1hz60deg_2.mfprof", "15p_1hz90deg_2.mfprof", "15p_1hz120deg.mfprof"]
# files = ["20p_1hz90deg.mfprof","20p_1hz120deg.mfprof","20p_1hz60deg.mfprof","20p_05hz120deg.mfprof","20p_05hz90deg.mfprof","20p_05hz150deg.mfprof",]
# files = ["25p_1hz90deg.mfprof","25p_1hz120deg.mfprof","25p_1hz60deg.mfprof","25p_05hz120deg.mfprof","25p_05hz90deg.mfprof","25p_05hz150deg.mfprof",]
files = ["30p_1hz120deg_2.mfprof","30p_1hz60deg.mfprof","30p_1hz90deg.mfprof","30p_05hz90deg.mfprof","30p_05hz150deg.mfprof","30p_05hz120deg.mfprof",]

plt.figure(figsize=(7, 6))
# 设置坐标轴刻度线条粗度
plt.rcParams['axes.linewidth'] = 3
plt.tick_params(axis='both', which='both', width=1.5, length=6)
plt.xlabel(r'Shear Rate $\gamma_{\mathrm{eff}}$ ')
plt.ylabel(r'Viscosity $\nu_{\mathrm{eff}}$')
plt.ylim(0, 800)
plt.xlim(5,12)
Visc = []
Shear_rate = []
Coord = []
for file in files:
    data = uvp.readUvpFile(file)
    # data.redefineSoundSpeed(1029)
    vel_origin = data.velTables[0]
    coords_origin = data.coordinateArrays[0]
    analysis = data.createUSRAnalysis()
    analysis.channelRange(87, 97)
    analysis.cylinderGeom(77, 106.77, 10.62)

    analysis.slicing(20)

    shearrate, visc = analysis.rheologyViscosity(smooth_level=9, ignoreException=True)
    plt.scatter(shearrate, visc, s=5, alpha=0.3, label=file, color = "black")
    Visc.extend(list(visc))
plt.axhline(y=np.average(Visc), color='red', linestyle='--',linewidth=2.5)
print(np.average(Visc))
print(np.min(Visc))
print(np.max(Visc))
plt.show()


Visc = np.array(Visc)
ave = np.average(Visc,axis = 0)

