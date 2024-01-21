import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from pyuvp import ForMetflowUvp



CHOOSE = 0

if CHOOSE == 0:
    File  = ['5p-65duty.mfprof','5p-70duty.mfprof','5p-75duty.mfprof','5p-80duty.mfprof']
    miu = [1,2,3,4]
    delta_P = [1,2,3,4]



Rudio = 0.025
L = 0.46

for i,file in enumerate(File):
    data = ForMetflowUvp.readUvpFile(file)
    data.defineSoundSpeed(1005)


    def velosity_perfile(r, miu):
        return delta_P[i] / (4 * miu * L) * (Rudio ** 2 - (r) ** 2)

    vel = data.velTables[0] * 2
    coords_origin = data.coordinateArrays[0] * np.cos(30 / 180 * np.pi)
    coords_origin = coords_origin - 28.7
    coords = coords_origin[11:165]
    vel = np.mean(vel, axis=0)
    vel = vel[11:165]


    plt.scatter(coords / 1000, vel / 1000)
    plt.plot(coords / 1000, velosity_perfile(coords / 1000, miu[i]))

    print('===============================')
    plt.grid()
    plt.show()
