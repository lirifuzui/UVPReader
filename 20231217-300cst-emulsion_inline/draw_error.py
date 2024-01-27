import matplotlib.pyplot as plt
import numpy as np

from pyuvp import ForMetflowUvp

plt.figure(figsize=(5.2, 6))
# 设置坐标轴刻度线条粗度
plt.rcParams['axes.linewidth'] = 3
plt.tick_params(axis='both', direction='in', which='both', width=1.5, length=6)
plt.ylim(0,0.016)
plt.xticks(np.arange(0, 5, 1))

error1 = [0.0029077636771662947,
          0.00556060448066218,
          0.006528222140679023,
          0.006563282768512409]
error2 = [0.00514319232877722,
          0.007210449569945043,
          0.007708178623230622,
          0.007599374952076393]
error3 = [0.003957933033653677,
          0.006284346324128336,
          0.008271213445600929,
          0.008390912498841416]
error4 = [0.004075368210025448,
          0.007568467399248142,
          0.009546065953795212,
          0.010158437342120968]
error5 = [0.0048989008879715325,
          0.008429195561873264,
          0.011083745693020553,
          0.011851584715081144]
colors = ['#8c564b','#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
x = [0,1,2,3]
x2 = [1,2,3,4]
plt.scatter(x2, error1,marker='*',color = colors[0],label = '-')
plt.plot(x2, error1,linestyle = '--',color = colors[0],label = '-')
plt.scatter(x2, error2,marker='o',color = colors[1],label = '-')
plt.plot(x2, error2,linestyle = '--',color = colors[1],label = '-')
plt.scatter(x2, error3,marker='s',color = colors[2],label = '-')
plt.plot(x2, error3,linestyle = '--',color = colors[2],label = '-')
plt.scatter(x2, error4,marker='v',color = colors[3],label = '-')
plt.plot(x2, error4,linestyle = '--',color = colors[3],label = '-')
plt.scatter(x, error5,marker='p',color = colors[4],label = '-')
plt.plot(x, error5,linestyle = '--',color = colors[4],label = '-')


plt.legend()

plt.show()
