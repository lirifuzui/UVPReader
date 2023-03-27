import pyuvp as uvp
import matplotlib.pyplot as plt

# example of single tdx.

# Read the data in the ".mfprof" file
data = uvp.ReadData(r'C:\Users\ZHENG WENQING\Desktop\UVPReader\UVPdatas\0.5hz90deg.mfprof')

# Extract datas.
vel_data = data.velTables[0]
echo_data = data.echoTables[0]
times = data.timeSeries[0]
coordinate_series = data.coordinateSeries[0]
# Another way.
vel_data = data.datas["vel_data"][0]
echo_data = data.datas["echo_data"][0]
times = data.datas["times"][0]
coordinate_series = data.datas["coords"][0]

# create an analysis from data.
anaylsis = data.createAnalysis()
# Another way.
analysis = uvp.Analysis(data)
# do fft
max_magnitude, phase_delay, phase_delay_derivative, real_part, imag_part = anaylsis.do_fft()

plt.figure()
plt.plot(coordinate_series, phase_delay)
plt.show()
