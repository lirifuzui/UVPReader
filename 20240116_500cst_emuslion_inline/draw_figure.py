import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from pyuvp import ForMetflowUvp

plt.figure(figsize=(4.5, 6))
# 设置坐标轴刻度线条粗度
plt.rcParams['axes.linewidth'] = 3
plt.tick_params(axis='both', direction='in',which='both', width=1.5, length=6)
plt.ylim(0, 0.2)
plt.xlim(-0.025, 0.025)
plt.xlabel(r'R')
plt.ylabel(r'V')

CHOOSE = -1


if CHOOSE == -1:
    File  = ['10p_60duty.mfprof','10p_65duty.mfprof','10p_70duty.mfprof','10p_75duty.mfprof','10p_80duty.mfprof']
    miu = [0.639,0.594,0.607,0.578,0.603]
    delta_P = [115,167.83,238.21,280.02,338.84]

if CHOOSE == 0:
    File  = ['15p-65duty.mfprof','15p-70duty.mfprof','15p-75duty.mfprof','15p-80duty.mfprof']
    miu = [0.467,0.427,0.391,0.403]
    delta_P = [125.4,160.62,189.51,227.85]

if CHOOSE == 1:
    File  = ['20p-65duty.mfprof','20p-70duty.mfprof','20p-75duty.mfprof','20p-80duty.mfprof']
    miu = [0.556,0.461,0.421,0.437]
    delta_P = [145.7,170.16,201.30,241.88]

if CHOOSE == 2:
    File = ['25p-65duty.mfprof', '25p-70duty.mfprof', '25p-75duty.mfprof', '25p-80duty.mfprof']
    miu = [0.601, 0.548, 0.531, 0.514]
    delta_P = [155.094, 200.021, 248.153, 281.505]

if CHOOSE == 3:
    File = ['30p-60duty.mfprof', '30p-65duty.mfprof', '30p-70duty.mfprof', '30p-75duty.mfprof']
    miu = [0.651, 0.613, 0.601, 0.674]
    delta_P = [109.51, 158.58, 211.11, 304.66]


colors = ['#8c564b','#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

Rudio = 0.025
L = 0.46

for i,file in enumerate(File):
    data = ForMetflowUvp.readUvpFile(file)




    def velosity_perfile(r, miu):
        return delta_P[i] / (4 * miu * L) * (Rudio ** 2 - (r) ** 2)

    vel = data.velTables[0] * 2
    coords_origin = data.coordinateArrays[0] * np.cos(30 / 180 * np.pi)
    coords_origin = coords_origin - 30
    coords = coords_origin[11:165]
    vel = np.mean(vel, axis=0)
    vel = vel[11:165]


    plt.scatter(coords / 1000, vel / 1000, s=8, alpha=0.7, label=file,color = colors[i])
    plt.plot(coords / 1000, velosity_perfile(coords / 1000, miu[i]),color = colors[i], label=file)

print('===============================')
# plt.grid()
# plt.legend()
plt.show()
