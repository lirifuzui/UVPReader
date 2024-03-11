import matplotlib.pyplot as plt
import numpy as np

files = ["05hz60deg.mfprof", "05hz75deg.mfprof", "10p_05hz90deg.mfprof", "05hz105deg.mfprof", "10p_05hz120deg.mfprof"
    , "05hz135deg.mfprof", "10p_05hz150deg.mfprof"]
plt.figure()
plt.xlabel(r'Shear Rate $\gamma_{\mathrm{eff}}$ ')
plt.ylabel(r'Viscosity $\nu_{\mathrm{eff}}$')
plt.ylim(0, 3000)

for file in files:
    data = uvp.readFile(file)
    data.defineSoundSpeed(1066)
    vel_origin = data.velTables[0]
    coords_origin = data.coordinateArrays[0]
    analysis = data.createUSRAnalysis()
    analysis.cylinderGeom(72.5, 16.09, 11.115)
    analysis.channelRange(25, 55)
    analysis.slicing(40)
    analysis.sliceSize(7000)

    u_theta = analysis.velTableTheta()
    coordinates_r = analysis.coordSeries
    times = analysis.timeArrays()
    visc, shearrate = analysis.viscosity(smooth_level=9, ignoreException=True)

    visc_t = visc.reshape((41, 30))
    shearrate_t = shearrate.reshape((41, 30))
    visc = np.sum(visc_t, axis=0) / 41
    shearrate = np.sum(shearrate_t, axis=0) / 41
    plt.scatter(shearrate, visc, label=file)
    # plt.scatter(shearrate, visc, s=5, alpha=0.2, label=file)

plt.grid()
plt.legend()
plt.show()
