import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from pyuvp import ForMetflowUvp

plt.figure(figsize=(5, 6))
# 设置坐标轴刻度线条粗度
plt.rcParams['axes.linewidth'] = 3
plt.tick_params(axis='both', direction='in',which='both', width=1.5, length=6)
plt.xlabel(r'R')
plt.ylabel(r'V')

CHOOSE = 0

if CHOOSE == 0:
    File  = ['5p-65duty.mfprof','5p-70duty.mfprof','5p-75duty.mfprof','5p-80duty.mfprof']
    miu = [0.438,0.419,0.391,0.403]
    delta_P = [120.53,160.62,191.51,230.08]

colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

Rudio = 0.025
L = 0.46

for i,file in enumerate(File):
    data = ForMetflowUvp.readFile(file)
    data._data_show(2000)




    def velosity_perfile(r, miu):
        return delta_P[i] / (4 * miu * L) * (Rudio ** 2 - (r) ** 2)

    vel = data.velTables[0] * 2
    coords_origin = data.coordinateArrays[0] * np.cos(30 / 180 * np.pi)
    coords_origin = coords_origin - 29.3
    coords = coords_origin[11:165]
    vel = np.mean(vel, axis=0)
    vel = vel[11:165]


    plt.scatter(coords / 1000, vel / 1000, s=8, alpha=0.7, label=file,color = colors[i])
    plt.plot(coords / 1000, velosity_perfile(coords / 1000, miu[i]),color = colors[i])

print('===============================')
# plt.grid()
plt.show()
