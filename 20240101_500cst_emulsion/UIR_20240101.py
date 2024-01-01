import matplotlib.pyplot as plt
import numpy as np

from pyuvp import ForMetflowUvp

files = ['5p05hz5090.mfprof']

Visc = []
for file in files:
    data = ForMetflowUvp.readUvpFile(file)
    # data.redefineSoundSpeed(1029)
    vel_origin = data.velTables[0]
    coords_origin = data.coordinateArrays[0]
    analysis = data.createUSRAnalysis(num_processes=1)
    analysis.channelRange(16, 70)
    analysis.pipeGeom(30, 25, 5.16, 0.5)

    analysis.slicing(50)

    visc, shearrate = analysis.rheologyViscosity(min_viscosity=200, max_viscosity=1500, smooth_level=13,
                                                 ignoreException=True)
    plt.scatter(shearrate, visc, s=5, alpha=0.3, label=file, color="black")
    Visc.extend(visc)
    coord = analysis.coordSeries
std_deviation = np.std(np.array(Visc))
plt.axhline(y=np.average(Visc) + std_deviation, color='green', linestyle='--')
plt.axhline(y=np.average(Visc) - std_deviation, color='green', linestyle='--')
plt.axhline(y=np.average(Visc), color='red', linestyle='--')

# plt.grid()
# plt.legend()
plt.show()

Visc = np.array(Visc)
print(np.average(Visc))
ave = np.average(Visc, axis=0)
