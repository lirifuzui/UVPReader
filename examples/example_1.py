from pyuvp import uvpreader, usr
import matplotlib.pyplot as plt
import numpy as np

# example of single tdx.
# Viscosity analysis using USR, 1 Hz_120 deg.
# Read the data in the ".mfprof" file
data = uvpreader.ReadData(r'example_1.mfprof')   # 'data' is an instantiate object, cannot be print
# The sound speed can be corrected by the function 'resetSoundSpeed'.
data.resetSoundSpeed(980)


# -------------------------------------------------------------
# return datas.
use_mux = data.muxStatus                                # return 'OFF'

u_xi = data.velTables(tdx_num=0)                        # return a two-dimensional numpy matrix
echo = data.echoTables(tdx_num=0)                       # return a two-dimensional numpy matrix
times = data.timeSeries(tdx_num=0)                      # return a one-dimensional numpy matrix
coordinates_xi = data.coordinateSeries(tdx_num=0)       # return a one-dimensional numpy matrix


# -------------------------------------------------------------
# create an analysis from data.
analysis = data.createUSRAnalysis()  # 'anaylsis' is an instantiate object, cannot be print
# Another way.
analysis = usr.Analysis(data)

# Define cylinder dimensions
# cylinder radius[mm], The coordinate[mm] of the cylinder wall in the xi coordinate system, delta_y[mm]
analysis.settingOuterCylinder(72.5, 56.2, 13)

# return geometry.
# returns None if analysis.settingOuterCylinder is not run.
cylinder_r, delta_y = analysis.geometry

# Return u_theta, coordinates_r, times
# returns u_xi and coordinates_xi if analysis.settingOuterCylinder is not run.
u_theta = analysis.velTableTheta(window_num=0)          # return a two-dimensional numpy matrix
coordinates_r = analysis.coordinatesR(window_num=0)     # return a one-dimensional numpy matrix
times = analysis.timeSeries(window_num=0)  # return a one-dimensional numpy matrix

# According to the location, extract data that can be analyzed.
analysis.extractValidData(33, 60)

analysis.dataSlice()

# do fft
vibration_frequency, max_magnitude, phase_delay, phase_delay_derivative, real_part, imag_part = analysis.doFFT(
    window_num=0)

# Calculate effective shear rate and viscosity.
viscosity, shear_rate = analysis.calculate_Viscosity_ShearRate()
# Return shear rate and viscosity.
shear_rate = analysis.shearRate
viscosity = analysis.viscosity

# -------------------------------------------------------------
plt.figure()
plt.xlabel('R')
plt.ylabel('t [s]')
plt.xlim(0.5, 1)
plt.contourf(coordinates_r/cylinder_r, times[0:100], u_theta[0:100, :])
plt.show()

plt.figure()
plt.xlabel(r'$ \phi(r)[\pi] $')
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