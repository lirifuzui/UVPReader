import matplotlib.pyplot as plt
import numpy as np

from pyuvp import ForMetflowUvp

files = ['sample_duty50-701hz.mfprof']

Visc = []
for file in files:
    data = ForMetflowUvp.readUvpFile(file)
    # data.redefineSoundSpeed(1029)
    vel_origin = data.velTables[0]
    coords_origin = data.coordinateArrays[0]
    analysis = data.createUSRAnalysis(num_processes=1)
    analysis.channelRange(50, 110)
    analysis.pipeGeom(30, 25, 4.7, 1)

    analysis.slicing(15)

    visc, shearrate = analysis.rheologyViscosity(min_viscosity=200, max_viscosity=1500, smooth_level=21,
                                                 ignoreException=True)
    plt.scatter(shearrate, visc, s=5, alpha=0.3, label=file, color="black")
    Visc.append(visc)
    coord = analysis.coordSeries
plt.axhline(y=np.average(Visc), color='red', linestyle='--')
# plt.grid()
# plt.legend()
plt.show()

Visc = np.array(Visc)
print(np.average(Visc))
ave = np.average(Visc, axis=0)
