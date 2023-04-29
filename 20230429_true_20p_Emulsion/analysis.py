import matplotlib.pyplot as plt

from pyuvp import uvp

# files = ["1hz30deg.mfprof","1hz45deg.mfprof","1hz60deg02.mfprof","05hz60deg02.mfprof","05hz90deg.mfprof","05hz120deg.mfprof","05hz150deg02.mfprof"]
# files = ["1hz30deg.mfprof","1hz45deg.mfprof","1hz60deg02.mfprof"]
# files = ["05hz60deg02.mfprof","05hz90deg.mfprof","05hz120deg.mfprof","05hz150deg.mfprof"]
files = ["05hz60deg.mfprof", "05hz90deg02.mfprof", "05hz120deg.mfprof", "05hz150deg.mfprof",
         "1hz30deg.mfprof"]
plt.figure()
plt.xlabel(r'Shear Rate $\gamma_{\mathrm{eff}}$ ')
plt.ylabel(r'Viscosity $\nu_{\mathrm{eff}}$')
plt.ylim(0, 3000)

for file in files:
    data = uvp.readData(file)
    data.resetSoundSpeed(1066)
    vel_origin = data.velTables[0]

    analysis = data.createUSRAnalysis()
    analysis.cylinderGeom(72.5, 59.5, 11.115)
    analysis.coordsClean(65, 95)
    analysis.timeSlicing(50)
    analysis.sliceSize(2000)

    u_theta = analysis.velTableTheta()
    coordinates_r = analysis.coordSeries
    times = analysis.timeSeries()
    visc, shearrate = analysis.calculate_Viscosity_ShearRate(smooth_level=9, ignoreException=True)

    plt.scatter(shearrate, visc, s=10, alpha=0.2, label=file)

plt.grid()
plt.legend()
plt.show()
