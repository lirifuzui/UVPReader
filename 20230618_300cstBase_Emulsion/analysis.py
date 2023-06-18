import matplotlib.pyplot as plt

from pyuvp import uvp

files = ["05hz90deg.mfprof", "05hz120deg_2.mfprof", "05hz150deg.mfprof", "1hz60deg.mfprof", "1hz90deg.mfprof",
         "1hz120deg.mfprof"]
plt.figure()
plt.xlabel(r'Shear Rate $\gamma_{\mathrm{eff}}$ ')
plt.ylabel(r'Viscosity $\nu_{\mathrm{eff}}$')
plt.ylim(0, 1000)
# plt.ylim(0, 3)
plt.xlim(4, 15)

for file in files:
    data = uvp.readUvpFile(file)
    # data.redefineSoundSpeed(1029)
    vel_origin = data.velTables[0]
    coords_origin = data.coordinateArrays[0]
    analysis = data.createUSRAnalysis()
    analysis.channelRange(80, 110)
    analysis.cylinderGeom(77, 106.77, 10.62)

    analysis.slicing(10)
    analysis.sliceSize(2000)
    shearrate, visc = analysis.rheologyViscosity(smooth_level=9, ignoreException=True)
    plt.scatter(shearrate, visc, s=5, alpha=0.3, label=file)

    '''analysis.slicing(5)
    analysis.sliceSize(3000)
    shearrate, viscoic, viscoelastic, _ = analysis.rheologyViscoelasticity(1000)
    plt.scatter(shearrate, viscoelastic, s=5, alpha=0.3, label=file)'''

plt.grid()
# plt.legend()
plt.show()
