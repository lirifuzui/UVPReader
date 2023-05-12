import matplotlib.pyplot as plt
import numpy as np

from pyuvp import uvp

files = ["05hz120deg.mfprof","1hz60deg.mfprof", "1hz60deg.mfprof",]
# files = ["1hz45deg.mfprof", "1hz45deg02.mfprof"]
# files = ["05hz60deg.mfprof","05hz90deg02.mfprof","05hz120deg.mfprof","05hz150deg.mfprof",]
# files = ["1hz30deg.mfprof","1hz45deg.mfprof","1hz60deg.mfprof",]
# files = ["05hz90deg.mfprof", "05hz90deg02.mfprof", "05hz90deg03.mfprof"]
# files = ["05hz150deg.mfprof", "05hz150deg02.mfprof"]
plt.figure()
plt.xlabel(r'Shear Rate $\gamma_{\mathrm{eff}}$ ')
plt.ylabel(r'Viscosity $\nu_{\mathrm{eff}}$')
plt.ylim(0, 3000)

for file in files:
    data = uvp.readData(file)
    data.redefineSoundSpeed(1066)
    vel_origin = data.velTables[0]

    analysis = data.createUSRAnalysis()
    analysis.cylinderGeom(72.5, 59.5, 11.115)
    analysis.channelRange(65, 95)
    analysis.slicing(40)
    analysis.sliceSize(7000)

    u_theta = analysis.velTableTheta()
    coordinates_r = analysis.coordSeries
    times = analysis.timeSeries()
    visc, shearrate = analysis.calculation(smooth_level=9, ignoreException=True)

    visc_t = visc.reshape((41,30))
    shearrate_t = shearrate.reshape((41,30))
    visc = np.sum(visc_t,axis=0)/41
    shearrate = np.sum(shearrate_t,axis=0)/41
    plt.scatter(shearrate, visc, label=file)
    #plt.scatter(shearrate, visc, s=5, alpha=0.2, label=file)

plt.grid()
plt.legend()
plt.show()
