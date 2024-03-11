import matplotlib.pyplot as plt
import numpy as np

from pyuvp import ForMetflowUvp

plt.figure(figsize=(5.2, 6))
# 设置坐标轴刻度线条粗度
plt.rcParams['axes.linewidth'] = 3
plt.tick_params(axis='both', direction='in', which='both', width=1.5, length=6)
plt.ylim(0,1.3)
ax = plt.gca()
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('right')
plt.xticks(np.arange(0, 5, 1))

refer_visc = np.array([1.2193,1.4157,1.6194,1.8505,2.1372]) * 300


visc10p = np.abs(np.array([0.639,0.594,0.607,0.578,0.603])*1000-refer_visc[0])/refer_visc[0]
visc15p = np.abs(np.array([0.769,0.751,0.694,0.708, 0.726])*1000-refer_visc[1])/refer_visc[1]
visc20p = np.abs(np.array([1.091,0.885,0.824,0.783, 0.767])*1000-refer_visc[2])/refer_visc[2]
visc25p = np.abs(np.array([0.952,0.912, 0.885, 0.951, 0.994])*1000-refer_visc[3])/refer_visc[3]
visc30p =  np.abs(np.array([1.087, 1.071, 1.114, 0.951, 0.975])*1000-refer_visc[4])/refer_visc[4]
colors = ['#8c564b','#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
x = [0,1,2,3, 4]
plt.scatter(x, visc10p,marker='*',color = colors[0],label = '-')
plt.plot(x, visc10p,linestyle = '--',color = colors[0],label = '-')
plt.scatter(x, visc15p,marker='o',color = colors[1],label = '-')
plt.plot(x, visc15p,linestyle = '--',color = colors[1],label = '-')
plt.scatter(x, visc20p,marker='s',color = colors[2],label = '-')
plt.plot(x, visc20p,linestyle = '--',color = colors[2],label = '-')
plt.scatter(x, visc25p,marker='v',color = colors[3],label = '-')
plt.plot(x, visc25p,linestyle = '--',color = colors[3],label = '-')
plt.scatter(x, visc30p,marker='p',color = colors[4],label = '-')
plt.plot(x, visc30p,linestyle = '--',color = colors[4],label = '-')


# plt.legend()

plt.show()
