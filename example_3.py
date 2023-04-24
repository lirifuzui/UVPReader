from pyuvp import uvp, usr
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# 读取 CSV 文件
df = pd.read_csv('u_xi500cSt1Hz90deg_vel.csv', header=None)

data = np.array(df.iloc[4:, 1:]).astype(float)
coords = np.array(df.iloc[3:4, 1:]).astype(float)[0]
times = np.array(df.iloc[4:, 0:1]).astype(float)
times = np.transpose(times)[0]

anaylsis = usr.Analysis(None, 0, [data], [times], [coords], ignoreException=False)
anaylsis.coordsClean(34, 46)
anaylsis.cylinderGeom(72.5, vibration_params=[1, 90])

vibration_frequency, max_magnitude, phase_delay, phase_delay_derivative, real_part, imag_part = anaylsis.doFFT()


time = anaylsis.timeSeries()[0:50]
cyclinder_r, detla_y = anaylsis.geometry
coordinates_r = anaylsis.coordSeries
u = np.transpose(anaylsis.velTableTheta())[:, 0:50]

plt.plot(phase_delay/(2*np.pi)*360,coordinates_r)
plt.show()

anaylsis.timeSlicing(5)
anaylsis.timeSlicing(1)
#anaylsis.timeSlicing(5)

plt.contourf(time, coordinates_r / cyclinder_r, u, cmap="bwr", levels=20)
plt.show()

# analysis.timeSlicing(5)
visc, shearrate = anaylsis.calculate_Viscosity_ShearRate(ignoreException=True)

plt.scatter(shearrate, visc)
plt.ylim(1500, 2500)
plt.grid()
plt.xlabel(r'Shear Rate $\gamma_{\mathrm{eff}}$ ')
plt.ylabel(r'Viscosity $\nu_{\mathrm{eff}}$')
plt.show()
