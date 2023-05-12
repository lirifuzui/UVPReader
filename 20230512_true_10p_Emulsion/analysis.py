import matplotlib.pyplot as plt

from pyuvp import uvp

# files = ["05hz90deg.mfprof", "05hz100deg.mfprof", "05hz110deg.mfprof", "05hz120deg.mfprof", "05hz130deg.mfprof", "05hz140deg.mfprof", "05hz150deg.mfprof", "05hz160deg.mfprof", "05hz170deg.mfprof"]
files = ["1hz45deg.mfprof", "1hz60deg.mfprof", "1hz70deg.mfprof", "1hz80deg.mfprof", "1hz90deg.mfprof",
         "1hz100deg.mfprof"]
# files = ["1hz45deg.mfprof","1hz60deg.mfprof","1hz70deg.mfprof","1hz80deg.mfprof","1hz90deg.mfprof","1hz100deg.mfprof","05hz90deg.mfprof", "05hz100deg.mfprof", "05hz110deg.mfprof", "05hz120deg.mfprof", "05hz130deg.mfprof","05hz140deg.mfprof", "05hz150deg.mfprof", "05hz160deg.mfprof", "05hz170deg.mfprof"]
plt.figure()
plt.xlabel(r'Shear Rate $\gamma_{\mathrm{eff}}$ ')
plt.ylabel(r'Viscosity $\nu_{\mathrm{eff}}$')
plt.ylim(500, 2500)

for file in files:
    data = uvp.readData(file)
    # data.redefineSoundSpeed(1029)
    vel_origin = data.velTables[0]
    coords_origin = data.coordinateSeries[0]
    analysis = data.createUSRAnalysis()
    analysis.channelRange(54, 75)
    analysis.cylinderGeom(72.5, 61.75, 11.115)
    analysis.slicing(10)
    analysis.sliceSize(500)

    u_theta = analysis.velTableTheta()
    coordinates_r = analysis.coordSeries
    times = analysis.timeSeries()
    visc, shearrate = analysis.calculation(smooth_level=9, ignoreException=True)

    '''visc_t = visc.reshape((6, 30))
    shearrate_t = shearrate.reshape((6, 30))
    visc = np.sum(visc_t, axis=0) / 41
    shearrate = np.sum(shearrate_t, axis=0) / 41
    plt.scatter(shearrate, visc, label=file)'''
    plt.scatter(shearrate, visc, s=5, alpha=0.3, label=file)

plt.grid()
# plt.legend()
plt.show()
