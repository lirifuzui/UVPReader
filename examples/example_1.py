import matplotlib.pyplot as plt
import numpy as np

from pyuvp import usr

# example of single tdx.
# Viscosity analysis using USR, 1 Hz_120 deg.
# Read the data in the ".mfprof" file
data = uvp.readUvpFile(r'example_1.mfprof')  # 'data' is an instantiate object, cannot be print
# The sound speed can be corrected by the function 'resetSoundSpeed'.
data.__multiplying_coefficient()

# -------------------------------------------------------------
# return datas.
use_mux = data.muxStatus  # return 'OFF'
u_xi = data.velTables[0]  # return a two-dimensional numpy matrix
echo = data.echoTables[0]  # return a two-dimensional numpy matrix
times = data.timeArrays[0]  # return a one-dimensional numpy matrix
coordinates_xi = data.coordinateArrays[0]  # return a one-dimensional numpy matrix

# -------------------------------------------------------------
# create an analysis from data.
analysis = data.createUSRAnalysis(tdx_num=0,
                                  ignoreException=False)  # 'analysis' is an instantiate object, cannot be print
# Another way.
analysis = usr.Analysis(data, ignoreException=False)

# -------------------------------------------------------------
# According to the location, extract data that can be analyzed.
analysis.channelRange(35, 60)

# Define cylinder dimensions
# cylinder radius[mm], The coordinate[mm] of the cylinder wall in the xi coordinate system, delta_y[mm]
'''analysis.settingOuterCylinder(72.5, 61, 12)'''
# Or enter the vibration parameters of cylinder,[frequency, amplitude]. 'Delta Y' and 'Vibration Params' must enter one.
# The function 'settingOuterCylinder' overwrites the original data with new data and can only be executed once.
analysis.cylinderGeom(72.5, vibration_params=[1, 120], ignoreException=False)

# Create a data slices. This function can divide the data into several equal parts according to time.
analysis.slicing(5)

# -------------------------------------------------------------
# return geometry.
# returns None if analysis.settingOuterCylinder is not run.
cylinder_r, delta_y = analysis.geometry

# Return u_theta, coordinates_r, times
# returns u_xi and coordinates_xi if analysis.settingOuterCylinder is not run.
# window_num=0，represents the complete data that has not been sliced
u_theta = analysis.velTableTheta(window_num=0)          # return a two-dimensional numpy matrix
coordinates_r = analysis.coordSeries                   # return a one-dimensional numpy matrix
times = analysis.timeSeries(window_num=0)               # return a one-dimensional numpy matrix

# do fft
vibration_frequency, max_magnitude, phase_delay, phase_delay_derivative, real_part, imag_part = analysis.fftInUSR(
    window_num=0)

# Calculate effective shear rate and viscosity.
viscosity, shear_rate = analysis.viscosity(30000, 1, 15, ignoreException=False)
# Return shear rate and viscosity.
shear_rate = analysis.shearRate
viscosity = analysis.viscosity
print(len(shear_rate),len(viscosity))

# -------------------------------------------------------------
# plot
u = np.transpose(u_theta[0:100, :])
time = times[0:100]
plt.figure()
plt.ylabel('R')
plt.xlabel('t [s]')
#plt.ylim(0.65, 1)
plt.contourf(time, coordinates_r/cylinder_r, u, cmap="bwr", levels=20)
plt.colorbar()
plt.show()

plt.figure()
plt.xlabel(r'$ \phi(r)[\pchoose_volume_f] $')
plt.ylabel(r'r/R')
plt.grid()
plt.plot(phase_delay*180/np.pi, coordinates_r/cylinder_r)
plt.show()

plt.figure()
plt.xlabel(r'$\frac{\mathrm{data} \phi}{\mathrm{data} r} $ ')
plt.ylabel(r'r/R')
plt.grid()
plt.plot(phase_delay_derivative, coordinates_r/cylinder_r)
plt.show()

plt.figure()
plt.xlabel(r'Shear Rate $\gamma_{\mathrm{eff}}$ ')
plt.ylabel(r'Viscosity $\nu_{\mathrm{eff}}$')
plt.ylim(0, 2000)
plt.grid()
plt.scatter(shear_rate, viscosity)
plt.show()