import matplotlib.pyplot as plt

from pyuvp import uvp

files = ["1hz90deg.mfprof", "1hz120deg.mfprof"]
plt.figure()
plt.xlabel(r'Shear Rate $\gamma_{\mathrm{eff}}$ ')
plt.ylabel(r'Viscosity $\nu_{\mathrm{eff}}$')
plt.ylim(500, 2500)
# plt.ylim(0, 3)
plt.xlim(1, 20)

for file in files:
    data = uvp.readUvpFile(file)
    # data.redefineSoundSpeed(1029)
    vel_origin = data.velTables[0]
    coords_origin = data.coordinateArrays[0]
    analysis = data.createUSRAnalysis()
    analysis.channelRange(35, 70)
    analysis.cylinderGeom(77, 35, 10.615)

    analysis.slicing(20)
    analysis.sliceSize(3000)
    shearrate, visc = analysis.rheologyViscosity(smooth_level=9, ignoreException=True)
    plt.scatter(shearrate, visc, s=5, alpha=0.3, label=file)

    '''analysis.slicing(20)
    analysis.sliceSize(5000)
    shearrate, viscoic, viscoelastic, _ = analysis.rheologyViscoelasticity(1000)
    plt.scatter(shearrate, viscoic, s=5, alpha=0.3, label=file)'''

plt.grid()
# plt.legend()
plt.show()
