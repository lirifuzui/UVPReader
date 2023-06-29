import matplotlib.pyplot as plt
import numpy as np

from pyuvp import uvp

files = ["10p_05hz90deg.mfprof", "05hz105deg.mfprof", "10p_05hz120deg.mfprof", "05hz135deg.mfprof", "10p_05hz150deg.mfprof",
         "10p_1hz60deg.mfprof", "1hz65deg.mfprof", "1hz75deg.mfprof", "1hz80deg.mfprof", "10p_1hz90deg.mfprof"]
# files = ["10p_05hz90deg.mfprof", "05hz105deg.mfprof", "10p_05hz120deg.mfprof", "05hz135deg.mfprof", "10p_05hz150deg.mfprof"]
# files = ["10p_1hz60deg.mfprof", "1hz65deg.mfprof", "1hz75deg.mfprof", "1hz80deg.mfprof", "10p_1hz90deg.mfprof"]
# files = ["day2-10p_1hz60deg.mfprof", "day2-10p_1hz90deg.mfprof", "day2-10p_1hz120deg.mfprof", "day2-1hz75deg.mfprof","day2-1hz105deg.mfprof"]
# files = ["day2-10p_05hz90deg.mfprof", "day2-10p_05hz120deg.mfprof", "day2-10p_05hz150deg.mfprof", ]
# files = ["day3-10p_1hz60deg.mfprof", "day3-10p_1hz90deg.mfprof", "day3-10p_1hz120deg.mfprof"]
# files = ["day3-10p_05hz90deg.mfprof", "day3-10p_05hz120deg.mfprof", "day3-10p_05hz150deg.mfprof", ]
# files = ["day3-15hz60deg.mfprof", "day3-15hz75deg.mfprof", "day3-15hz90deg.mfprof", ]
plt.figure()
plt.xlabel(r'Shear Rate $\gamma_{\mathrm{eff}}$ ')
plt.ylabel(r'Viscosity $\nu_{\mathrm{eff}}$')
plt.ylim(800, 1800)
# plt.ylim(0, 3)
plt.xlim(1, 7)
VISC = []
for file in files:
    data = uvp.readUvpFile(file)
    # data.redefineSoundSpeed(1029)
    vel_origin = data.velTables[0]
    coords_origin = data.coordinateArrays[0]
    analysis = data.createUSRAnalysis()
    analysis.channelRange(70, 95)
    analysis.cylinderGeom(77, 79, 10.615)

    analysis.slicing(5)
    analysis.sliceSize(3000)
    shearrate, visc = analysis.rheologyViscosity(smooth_level=9, ignoreException=True)
    plt.scatter(shearrate, visc, s=5, alpha=0.3, label=file)
    VISC.extend(visc)
    '''analysis.slicing(5)
    analysis.sliceSize(3000)
    shearrate, viscoic, viscoelastic, _ = analysis.rheologyViscoelasticity(1000)
    plt.scatter(shearrate, viscoelastic, s=5, alpha=0.3, label=file)'''
print(np.average(VISC))
plt.grid()
# plt.legend()
plt.show()

