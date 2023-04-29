import matplotlib.pyplot as plt

from pyuvp import uvp

files = ["1hz30deg.mfprof","1hz45deg.mfprof","1hz60deg02.mfprof","05hz60deg02.mfprof","05hz90deg.mfprof","05hz120deg.mfprof","05hz150deg.mfprof"]
# files = ["1hz30deg.mfprof","1hz45deg.mfprof","1hz60deg02.mfprof"]
# files = ["05hz60deg02.mfprof","05hz90deg.mfprof","05hz120deg.mfprof","05hz150deg.mfprof"]
# files = ["05hz60deg.mfprof","05hz60deg02.mfprof","05hz60deg03.mfprof"]
plt.figure()
plt.xlabel(r'Shear Rate $\gamma_{\mathrm{eff}}$ ')
plt.ylabel(r'Viscosity $\nu_{\mathrm{eff}}$')
plt.ylim(500, 2000)

for file in files:
    data = uvp.readData(file)
    data.redefineSoundSpeed(1029)
    vel_origin = data.velTables[0]

    analysis = data.createUSRAnalysis()
    analysis.cylinderGeom(72.5, 71.54, 11.35)
    analysis.coordsClean(55, 90)
    analysis.timeSlicing(50)
    u_theta = analysis.velTableTheta()
    coordinates_r = analysis.coordSeries
    times = analysis.timeSeries()

    visc, shearrate = analysis.calculate_Viscosity_ShearRate(smooth_level= 9,ignoreException=True)
    '''visc_t = visc.reshape((51,35))
    shearrate_t = shearrate.reshape((51,35))
    visc = np.sum(visc_t,axis=0)/11
    shearrate = np.sum(shearrate_t,axis=0)/11'''

    plt.scatter(shearrate, visc, s=10, alpha=0.1, label=file)


plt.grid()
plt.legend()
plt.show()
