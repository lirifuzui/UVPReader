import pyuvp as uvp
import matplotlib.pyplot as plt

import numpy as np

# example of single tdx.

# Read the data in the ".mfprof" file
data = uvp.ReadData(r'1hz_120deg.mfprof')   # 'data' is an instantiate object, cannot be print
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
analysis = data.createAnalysis()                        # 'anaylsis' is an instantiate object, cannot be print
# Another way.
analysis = uvp.Analysis(data)

# According to the location, extract data that can be analyzed.
analysis.extract_analyzable_data([31, 58])

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
times = analysis.timeSlice(window_num=0)                # return a one-dimensional numpy matrix

# do fft
max_magnitude, phase_delay, phase_delay_derivative, real_part, imag_part = analysis.do_fft(window_num=0)
# Calculate effective shear rate.
shear_rate = analysis.calculate_effective_shear_rate(window_num=0)

shear_rate = analysis.shearRate


# -------------------------------------------------------------
plt.figure()
plt.xlabel('R')
plt.ylabel('t [s]')
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

