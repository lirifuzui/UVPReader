from pyuvp import uvp, usr
import matplotlib.pyplot as plt
import numpy as np

data = uvp.readData("1hz30deg.mfprof")
analysis = data.createUSRAnalysis()

analysis.validVelData(20, 60)
analysis.settingOuterCylinder(72.5, 41,11.7)
u_theta = analysis.velTableTheta()
coordinates_r = analysis.coordSeries
times = analysis.timeSeries()

visc, shearrate = analysis.calculate_Viscosity_ShearRate()


u = np.transpose(u_theta[0:100, :])
time = times[0:100]
plt.figure()
plt.ylabel('R')
plt.xlabel('t [s]')
#plt.ylim(0.65, 1)
plt.contourf(time, coordinates_r, u, cmap="bwr", levels=20)
plt.colorbar()
plt.show()


plt.figure()
plt.xlabel(r'Shear Rate $\gamma_{\mathrm{eff}}$ ')
plt.ylabel(r'Viscosity $\nu_{\mathrm{eff}}$')
plt.ylim(0, 1000)
plt.grid()
plt.scatter(shearrate, visc)
plt.show()
