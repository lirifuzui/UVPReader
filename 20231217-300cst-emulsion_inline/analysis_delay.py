import matplotlib.pyplot as plt
import numpy as np

from pyuvp import ForMetflowUvp

files = ['10p-10hz-5070duty.mfprof','10p-05hz-5070duty.mfprof']

plt.figure()
# 设置坐标轴刻度线条粗度
plt.rcParams['axes.linewidth'] = 3
plt.tick_params(axis='both', which='both', width=1.5, length=6)
plt.xlabel(r'Shear Rate $\gamma_{\mathrm{eff}}$ ')
plt.ylabel(r'Viscosity $\nu_{\mathrm{eff}}$')
plt.ylim(0, 800)
# plt.xlim(5, 12)
Visc = []
for file in files:
    data = ForMetflowUvp.readUvpFile(file)
    # data.redefineSoundSpeed(1029)
    vel_origin = data.velTables[0]
    coords_origin = data.coordinateArrays[0]
    analysis = data.createUSRAnalysis(num_processes=1)
    analysis.channelRange(25, 80)
    analysis.pipeGeom(30, 25, 4.7, 1)

    analysis.slicing(20)

    visc, shearrate = analysis.rheologyViscosity(min_viscosity=100, max_viscosity=1000, smooth_level=21,
                                                 ignoreException=True)
    plt.scatter(shearrate, visc, s=5, alpha=0.3, label=file, color="black")
    Visc.extend(visc)
    coord = analysis.coordSeries
plt.axhline(y=np.average(Visc), color='red', linestyle='--')
# plt.grid()
# plt.legend()
plt.show()

Visc = np.array(Visc)
print(np.average(Visc))
ave = np.average(Visc, axis=0)
'''y_r = ave/300
k = 1/300
phi_m = 0.637
y = y_r*((2*y_r + 5*k)/(2+5*k))**(3/2)
phi_FA = phi_m/((9/(8*y)+1)**3)
plt.figure()
plt.plot(coord ,phi_FA)
plt.show()'''
