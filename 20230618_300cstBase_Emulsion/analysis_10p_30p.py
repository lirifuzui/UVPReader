import matplotlib.pyplot as plt
import numpy as np
from pyuvp import ForMetflowUvp

File = [
    ["10p_05hz90deg.mfprof","10p_05hz120deg.mfprof","10p_05hz150deg.mfprof", "10p_1hz60deg.mfprof", "10p_1hz90deg.mfprof", "10p_1hz120deg.mfprof"],
    ["15p_05hz90deg.mfprof", "15p_05hz120deg.mfprof","15p_1hz60deg_2.mfprof","15p_1hz90deg_2.mfprof", "15p_05hz150deg.mfprof",  "15p_1hz120deg.mfprof"],
    ["20p_1hz90deg.mfprof","20p_1hz120deg.mfprof","20p_1hz60deg.mfprof","20p_05hz120deg.mfprof","20p_05hz90deg.mfprof","20p_05hz150deg.mfprof",],
    ["25p_05hz90deg.mfprof", "25p_05hz120deg.mfprof","25p_1hz90deg.mfprof", "25p_05hz150deg.mfprof",  "25p_1hz120deg.mfprof"],
    ["30p_1hz90deg.mfprof","30p_1hz120deg.mfprof","30p_1hz60deg.mfprof","30p_05hz90deg.mfprof","30p_05hz150deg.mfprof","30p_05hz120deg.mfprof",],
    ["35p_1hz90deg.mfprof","35p_1hz120deg.mfprof","35p_1hz60deg.mfprof"]
]

plt.figure(figsize=(5, 6))
# 设置坐标轴刻度线条粗度
plt.rcParams['axes.linewidth'] = 3
plt.tick_params(axis='both', direction='in',which='both', width=1.5, length=6)
plt.xlabel(r'x')
plt.ylabel(r'y')

plt.ylim(200, 800)
#plt.xlim(16, 24)

result = []
files = File[5]
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
    analysis.slicing(15)
    u_theta = analysis.velTableTheta()
    coordinates_r = analysis.coordSeries
    visc, shearrate = analysis.rheologyViscosity(smooth_level=9, ignoreException=True)

    #plt.scatter(shearrate, visc, s=5, alpha=0.3, label=file)
    plt.scatter(shearrate, visc, s=5, alpha=0.3, label=file, color = "black")
    Visc.extend(visc)

mean_V = np.average(Visc)
plt.axhline(y=mean_V, color='red', linestyle='--', label='Mean')
# plt.grid()
# plt.legend()
plt.show()