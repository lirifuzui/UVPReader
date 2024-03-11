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

CHOOSE = 3
offset = 28.7

if CHOOSE == -1:
    File  = ['10p_60duty.mfprof','10p_65duty.mfprof','10p_70duty.mfprof','10p_75duty.mfprof','10p_80duty.mfprof']
    miu = [0.639,0.594,0.607,0.578,0.603]
    delta_P = [115,167.83,238.21,280.02,338.84]

if CHOOSE == 0:
    File  = ['15p_60duty.mfprof','15p_65duty.mfprof','15p_70duty.mfprof','15p_75duty.mfprof','15p_80duty.mfprof']
    miu = [0.769,0.751,0.694,0.708, 0.726]
    delta_P = [138.00,207.34,269.06,334.6,401.9]

if CHOOSE == 1:
    File  = ['20p_60duty.mfprof','20p_65duty.mfprof','20p_70duty.mfprof','20p_75duty.mfprof','20p_80duty.mfprof']
    miu = [1.091,0.885,0.824,0.783, 0.767]
    delta_P = [190.76,240.8,319.7,365.44, 420.05]

if CHOOSE == 2:
    File = ['25p_60duty.mfprof','25p_65duty.mfprof', '25p_70duty.mfprof', '25p_75duty.mfprof', '25p_80duty.mfprof']
    miu = [0.952,0.912, 0.885, 0.824, 0.843]
    delta_P = [158.01, 238.93, 334.65, 377.34, 453.17]

if CHOOSE == 3:
    File = ['30p_60duty.mfprof', '30p_65duty.mfprof', '30p_70duty.mfprof', '30p_75duty.mfprof', '30p_80duty.mfprof']
    miu = [1.087, 1.071, 1.114, 0.951, 0.975]
    delta_P = [174.35, 275.92, 393.98, 418.57, 508.49]


colors = ['#8c564b','#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

Rudio = 0.025
L = 0.46

for i,file in enumerate(File):
    data = ForMetflowUvp.readUvpFile(file)




    def velosity_perfile(r, miu):
        return delta_P[i] / (4 * miu * L) * (Rudio ** 2 - (r) ** 2)

    vel = data.velTables[0] * 2
    coords_origin = data.coordinateArrays[0] * np.cos(30 / 180 * np.pi)
    coords_origin = coords_origin - offset
    coords = coords_origin[14:125]
    vel = np.mean(vel, axis=0)
    vel = vel[14:125]


    plt.scatter(coords[::3] / 1000, vel[::3] / 1000, s=24, alpha=0.7, label=file,color = colors[i], marker = "o")
    plt.plot(coords / 1000, velosity_perfile(coords / 1000, miu[i]),color = colors[i], label=file)

    vel_curve = velosity_perfile(coords / 1000, miu[i])
    vel_error = np.square(np.array(vel_curve-vel / 1000))
    error_mean = np.mean(vel_error)
    print(np.sqrt(error_mean))

print('===============================')
# plt.grid()
# plt.legend()
plt.show()
