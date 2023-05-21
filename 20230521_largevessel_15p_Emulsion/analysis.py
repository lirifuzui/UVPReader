import matplotlib.pyplot as plt

from pyuvp import uvp

files = ["05hz90deg.mfprof", "05hz105deg.mfprof", "05hz120deg.mfprof", "05hz135deg.mfprof", "05hz150deg.mfprof"]

plt.figure()
plt.xlabel(r'Shear Rate $\gamma_{\mathrm{eff}}$ ')
plt.ylabel(r'Viscosity $\nu_{\mathrm{eff}}$')
# plt.ylim(500, 2500)

for file in files:
    data = uvp.readData(file)
    # data.redefineSoundSpeed(1029)
    vel_origin = data.velTables[0]
    coords_origin = data.coordinateSeries[0]
    analysis = data.createUSRAnalysis()
    analysis.channelRange(60, 100)
    analysis.cylinderGeom(77, 79, 10.615)
    analysis.slicing(20)
    analysis.sliceSize(5000)

    shearrate, visc = analysis.rheologyViscosity(smooth_level=9, ignoreException=True)

    # analysis.slicing(0)
    # shearrate, viscoic, elastic, _ = analysis.rheologyViscoelasticity(1000)

    '''visc_t = visc.reshape((6, 30))
    shearrate_t = shearrate.reshape((6, 30))
    visc = np.sum(visc_t, axis=0) / 41
    shearrate = np.sum(shearrate_t, axis=0) / 41
    plt.scatter(shearrate, visc, label=file)'''
    plt.scatter(shearrate, visc, s=5, alpha=0.3, label=file)

plt.grid()
# plt.legend()
plt.show()
