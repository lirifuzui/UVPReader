import matplotlib.pyplot as plt
import numpy as np

from pyuvp import ForMetflowUvp

plt.figure(figsize=(5.2, 6))
# 设置坐标轴刻度线条粗度
plt.rcParams['axes.linewidth'] = 3
plt.tick_params(axis='both', direction='in', which='both', width=1.5, length=6)
plt.ylim(0,0.016)
plt.xticks(np.arange(0, 5, 1))

error1 = [0.003924039386223681,
0.0051652090414612715,
0.006918979843714503,
0.0064415148590896525,
0.010561558008819036]
error2 = [0.0053079642266753435,
0.0072061990508786675,
0.010380460644810442,
0.013767694814876729,
0.014813179245971406]
error3 = [0.003692190715579416,
0.006244798523624147,
0.012068880198159944,
0.013968752150411438,
0.00949305111369239]
error4 = [0.0022968443149485028,
0.004840783552040632,
0.00902394116155524,
0.009576893968640128,
0.011310710782807733]
error5 = [0.0028942024866339014,
0.005332014017219597,
0.008371024892501302,
0.011315547801565736,
0.012917285689745433]
colors = ['#8c564b','#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
x2 = [0,1,2,3,4]
plt.scatter(x2, error1,marker='*',color = colors[0],label = '-')
plt.plot(x2, error1,linestyle = '--',color = colors[0],label = '-')
plt.scatter(x2, error2,marker='o',color = colors[1],label = '-')
plt.plot(x2, error2,linestyle = '--',color = colors[1],label = '-')
plt.scatter(x2, error3,marker='s',color = colors[2],label = '-')
plt.plot(x2, error3,linestyle = '--',color = colors[2],label = '-')
plt.scatter(x2, error4,marker='v',color = colors[3],label = '-')
plt.plot(x2, error4,linestyle = '--',color = colors[3],label = '-')
plt.scatter(x2, error5,marker='p',color = colors[4],label = '-')
plt.plot(x2, error5,linestyle = '--',color = colors[4],label = '-')




plt.show()
