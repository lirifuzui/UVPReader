import matplotlib.pyplot as plt
import numpy as np

from pyuvp import uvp

# files = ["1hz30deg.mfprof","1hz45deg.mfprof","1hz60deg02.mfprof","05hz60deg03.mfprof","05hz90deg.mfprof","05hz120deg.mfprof","05hz150deg.mfprof"]
# files = ["1hz30deg.mfprof","1hz45deg.mfprof","1hz60deg02.mfprof"]
# files = ["05hz60deg02.mfprof","05hz90deg.mfprof","05hz120deg.mfprof","05hz150deg.mfprof"]
files = ["05hz60deg.mfprof","05hz60deg02.mfprof","05hz60deg03.mfprof"]
plt.figure()
plt.xlabel(r'Shear Rate $\gamma_{\mathrm{eff}}$ ')
plt.ylabel(r'Viscosity $\nu_{\mathrm{eff}}$')
plt.ylim(500, 2000)

slice_num = 40

for file in files:
    data = uvp.readUvpFile(file)
    data.redefineSoundSpeed(1029)
    vel_origin = data.velTables[0]

    analysis = data.createUSRAnalysis()
    analysis.cylinderGeom(72.5, 71.54, 11.35)
    analysis.channelRange(55, 90)
    analysis.slicing(slice_num)
    analysis.sliceSize(5000)
    u_theta = analysis.velTableTheta()
    coordinates_r = analysis.coordSeries
    times = analysis.timeSeries()

    visc, shearrate = analysis.viscosity(smooth_level=9, ignoreException=True)
    visc_t = visc.reshape((slice_num + 1, 35))
    shearrate_t = shearrate.reshape((slice_num+1,35))
    visc = np.sum(visc_t,axis=0)/(slice_num+1)
    shearrate = np.sum(shearrate_t,axis=0)/(slice_num+1)
    plt.scatter(shearrate, visc, label=file)
    # plt.scatter(shearrate, visc, s=10, alpha=0.1, label=file)


plt.grid()
plt.legend()
plt.show()
