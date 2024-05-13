import matplotlib.pyplot as plt
import numpy as np

from pyuvp import ForMetflowUvp

plt.figure(figsize=(6.6, 6))
# 设置坐标轴刻度线条粗度
plt.rcParams['axes.linewidth'] = 3
plt.tick_params(axis='both', direction='in', which='both', width=1.5, length=6)
# plt.ylim(0,0.016)
plt.xticks(np.arange(0.10, 0.36, 0.05))
plt.yticks(np.arange(0.10, 0.36, 0.05))

refer_phi = np.array([0.1, 0.15, 0.2, 0.25, 0.3])


def phi(y_r):
    K = 1 / 300
    y = y_r*((2*y_r + 5*K)/(2+5*K))**(3/2)
    phi_m = 0.48
    return phi_m / (9 / (8 * y) + 1) ** 3


miu2 = np.array([0.421, 0.391, 0.383, 0.382])*1000/300
miu3 = np.array([0.467,0.427,0.391,0.403])*1000/300
miu4 = np.array([0.556,0.461,0.421,0.437])*1000/300
miu5 = np.array([0.601, 0.548, 0.531, 0.514])*1000/300
miu6 = np.array([0.651, 0.613, 0.601, 0.674])*1000/300
print(phi(miu2))
print(phi(miu3))
print(phi(miu4))
print(phi(miu5))
print(phi(miu6))


visc10p = np.abs(phi(miu2) - refer_phi[0]) / refer_phi[0]
visc15p = np.abs(phi(miu3) - refer_phi[1]) / refer_phi[1]
visc20p = np.abs(phi(miu4) - refer_phi[2]) / refer_phi[2]
visc25p = np.abs(phi(miu5) - refer_phi[3]) / refer_phi[3]
visc30p = np.abs(phi(miu6) - refer_phi[4]) / refer_phi[4]


print(np.mean(visc10p))
print(np.mean(visc15p))
print(np.mean(visc20p))
print(np.mean(visc25p))
print(np.mean(visc30p))

'''
[  
[   ]
'''

phi02Q = [0.30492785]
phi03Q = [0.14688731, 0.18514401, 0.25056091,0.2782759,0.28505765]
phi04Q = [ 0.12128102, 0.15197995, 0.180282 ,0.24524873, 0.2782759]
phi05Q = [0.11447715, 0.12128102 ,0.14688731, 0.23357314, 0.31583263]
phi06Q = [0.11362927,0.13152825,0.16041541,0.22137795]



colors = ['#8c564b','#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
x1 = [0.30]
x2 = [0.10,0.15,0.20,0.25]
x = [0.10,0.15,0.20,0.25, 0.30]

plt.scatter(x1, phi02Q,marker='*',color = colors[0],label = '-')
plt.scatter(x, phi03Q,marker='o',color = colors[1],label = '-')
plt.scatter(x, phi04Q,marker='s',color = colors[2],label = '-')
plt.scatter(x, phi05Q,marker='v',color = colors[3],label = '-')
plt.scatter(x2, phi06Q,marker='p',color = colors[4],label = '-')

plt.plot([0.1,0.40], [0.1,0.40],linestyle = '--',color ='black')


plt.legend()

plt.show()
