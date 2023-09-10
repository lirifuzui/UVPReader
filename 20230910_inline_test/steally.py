import matplotlib.pyplot as plt
import numpy as np

from pyuvp import uvp

files = ["emulsion08_duty60.mfprof", ]

for file in files:
    data = uvp.readUvpFile(file)
    # data.redefineSoundSpeed(1029)
    vel_origin = data.velTables[0]
    coords_origin = data.coordinateArrays[0] * np.cos(30 / 180 * np.pi)
    vel_ave = np.mean(vel_origin, axis=0)
    print(vel_ave)

    plt.plot(coords_origin, vel_ave)
    plt.show()
