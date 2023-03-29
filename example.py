import pyuvp as uvp
import matplotlib.pyplot as plt

import numpy as np

# example of single tdx.

# Read the data in the ".mfprof" file
data = uvp.ReadData(r'1hz_120deg.mfprof')   # 'data' is an instantiated class, cannot be print


# -------------------------------------------------------------
# return datas.
use_mux = data.muxStatus                    # return 'Off'

u_xi = data.velTables()                     # return a two-dimensional numpy matrix
echo = data.echoTables()                    # return a two-dimensional numpy matrix
times = data.timeSeries()                   # return a one-dimensional numpy matrix
coordinates_xi = data.coordinateSeries()    # return a one-dimensional numpy matrix


# -------------------------------------------------------------
# create an analysis from data.
analysis = data.createAnalysis()            # 'anaylsis' is an instantiated class, cannot be print
# Another way.
analysis = uvp.Analysis(data)

# Define cylinder dimensions
# cylinder radius[mm], The coordinate[mm] of the cylinder wall in the xi coordinate system, delta_y[mm]
u_theta, coordinates_r = analysis.settingOuterCylinder(72.5, 60, 13)

# Another way to return u_theta and coordinates_r
u_theta = analysis.velTable_theta           # return a two-dimensional numpy matrix
coordinates_r = analysis.coordinates_R      # return a one-dimensional numpy matrix

# do fft
max_magnitude, phase_delay, phase_delay_derivative, real_part, imag_part = analysis.do_fft()

