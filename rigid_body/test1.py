from pyuvp import uvp, usr
import matplotlib.pyplot as plt
import numpy as np

data = uvp.readData("05hz45deg.mfprof")
analysis = data.createUSRAnalysis()


analysis.settingOuterCylinder(72.5, 41, 11.7)
analysis.validVelData(40, 60)
u_theta = analysis.velTableTheta()
coordinates_r = analysis.coordSeries
times = analysis.timeSeries()
x = [i for i in range(len(coordinates_r))]

plt.plot(x, coordinates_r)
plt.show()

u = np.transpose(u_theta[0:100, :])
time = times[0:100]
plt.figure()
plt.ylabel('R')
plt.xlabel('t [s]')
#plt.ylim(0.65, 1)
plt.contourf(time, coordinates_r, u, cmap="bwr", levels=20)
plt.colorbar()
plt.show()

analysis.timeSlicing(4)
visc, shearrate = analysis.calculate_Viscosity_ShearRate(ignoreException=True)

plt.figure()
plt.xlabel(r'Shear Rate $\gamma_{\mathrm{eff}}$ ')
plt.ylabel(r'Viscosity $\nu_{\mathrm{eff}}$')
plt.ylim(0, 800)
plt.grid()
plt.scatter(shearrate, visc)
plt.show()
