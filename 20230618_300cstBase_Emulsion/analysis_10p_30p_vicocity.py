import matplotlib.pyplot as plt
import numpy as np

from pyuvp import ForMetflowUvp

files = ["10p_05hz90deg.mfprof", "10p_05hz120deg_2.mfprof", "10p_05hz150deg.mfprof", "10p_1hz60deg.mfprof",
         "10p_1hz90deg.mfprof", "10p_1hz120deg.mfprof"]
# files = ["15p_05hz90deg.mfprof","15p_05hz120deg.mfprof","15p_05hz150deg.mfprof","15p_1hz60deg_2.mfprof", "15p_1hz90deg_2.mfprof", "15p_1hz120deg.mfprof"]
# files = ["20p_1hz90deg.mfprof","20p_1hz120deg.mfprof","20p_1hz60deg.mfprof","20p_05hz120deg.mfprof","20p_05hz90deg.mfprof","20p_05hz150deg.mfprof",]
# files = ["25p_1hz90deg.mfprof","25p_1hz120deg.mfprof","25p_1hz60deg.mfprof","25p_05hz120deg.mfprof","25p_05hz90deg.mfprof","25p_05hz150deg.mfprof",]
# files = ["30p_1hz120deg_2.mfprof","30p_1hz60deg.mfprof","30p_05hz90deg.mfprof","30p_05hz150deg.mfprof","30p_05hz120deg.mfprof",]

plt.figure(figsize=(7, 6))
# 设置坐标轴刻度线条粗度
plt.rcParams['axes.linewidth'] = 3
plt.tick_params(axis='both', direction="in", which='both', width=2, length=10)
plt.xticks([10, 15, 20, 25])
plt.yticks([1, 1.5, 2.0, 2.5])
plt.xlabel(r'Shear Rate $\gamma_{\mathrm{eff}}$ ')
plt.ylabel(r'Viscosity $\nu_{\mathrm{eff}}$')
plt.ylim(1, 2.5)
plt.xlim(10, 25)
Visc = []
Shear_rate = []
Coord = []
for file in files:
    data = ForMetflowUvp.readUvpFile(file)
    # data.redefineSoundSpeed(1029)
    vel_origin = data.velTables[0]
    coords_origin = data.coordinateArrays[0]
    analysis = data.createUSRAnalysis()
    analysis.channelRange(87, 97)
    analysis.cylinderGeom(77, 106.77, 10.62)

    analysis.slicing(20)

    visc, shearrate = analysis.rheologyViscosity(smooth_level=9, ignoreException=True)
    plt.scatter(shearrate, visc / 300, s=5, alpha=0.3, label=file, color="black")
    Visc.extend(list(visc))
plt.axhline(y=np.average(Visc) / 300, color='red', linestyle='--', linewidth=2.5)
print(np.average(Visc) / 300)
print(np.min(Visc) / 300)
print(np.max(Visc) / 300)
plt.show()

Visc = np.array(Visc)
ave = np.average(Visc, axis=0)
