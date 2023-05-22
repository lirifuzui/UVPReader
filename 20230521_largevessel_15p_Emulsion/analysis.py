import matplotlib.pyplot as plt

from pyuvp import uvp

# files = ["05hz90deg.mfprof", "05hz105deg.mfprof", "05hz120deg.mfprof", "05hz135deg.mfprof", "05hz150deg.mfprof"]
# files = ["1hz60deg.mfprof", "1hz65deg.mfprof", "1hz75deg.mfprof", "1hz80deg.mfprof", "1hz90deg.mfprof"]
files = ["day2-1hz60deg.mfprof", "day2-1hz90deg.mfprof", "day2-1hz120deg.mfprof", ]
# files = ["day2-05hz90deg.mfprof", "day2-05hz120deg.mfprof", "day2-05hz150deg.mfprof", ]
plt.figure()
plt.xlabel(r'Shear Rate $\gamma_{\mathrm{eff}}$ ')
plt.ylabel(r'Viscosity $\nu_{\mathrm{eff}}$')
# plt.ylim(500, 2500)
plt.ylim(0, 3)
plt.xlim(1, 10)

for file in files:
    data = uvp.readData(file)
    # data.redefineSoundSpeed(1029)
    vel_origin = data.velTables[0]
    coords_origin = data.coordinateSeries[0]
    analysis = data.createUSRAnalysis()
    analysis.channelRange(65, 100)
    analysis.cylinderGeom(77, 79, 10.615)
    # analysis.slicing(20)
    # analysis.sliceSize(5000)

    # shearrate, visc = analysis.rheologyViscosity(smooth_level=9, ignoreException=True)
    # plt.scatter(shearrate, visc, s=5, alpha=0.3, label=file)

    analysis.slicing(20)
    # analysis.sliceSize(2500)
    shearrate, viscoic, elastic, _ = analysis.rheologyViscoelasticity(1000)
    plt.scatter(shearrate, elastic, s=5, alpha=0.3, label=file)

plt.grid()
# plt.legend()
plt.show()
