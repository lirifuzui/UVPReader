import pandas as pd
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt
import matplotlib as mpl


#定义容器尺寸
cylinder_r :float = 72.5
#定于测量线的位置
Delta_y : float = 15.5229

#===========================================================
#读取文件
#一定注意可以正确读取的文件的书写格式
data :pd.DataFrame = pd.read_csv('0.5hz120deg-svel.csv')

#===========================================================
#提取时间序列    
time_list :[float] = data['time'].values.tolist()
time_array :np.ndarray = np.array(time_list)
#
#计算采样数
N :int = len(time_list)
#计算采样间隔
Delta_T :float = (time_list[-1]-time_list[0])/N



#===========================================================
#提取并计算圆周速度序列
velocity_list :[np.ndarray] = []
columns = data.columns
position_r_list :float = []
for c in columns:
    if c == 'time': continue
    position_r_list.append(float(c)) #记录采样坐标
    d = data[c].values.tolist()
    velocity_list.append(np.array([i*float(c)/Delta_y for i in d]))
#输出array形式的采样坐标和时空速度分布
position_r_array :np.ndarray = np.array(position_r_list)
velocity_array :np.ndarray = np.array(velocity_list)




   
#采用对单位时间的速度剖面进行函数拟合的方法消除噪音
from numpy import polyfit,poly1d
new_array = np.zeros((len(position_r_array),len(time_array)))
for n in range(len(time_array)):
    v_line = velocity_array[:,n]
    p = polyfit(position_r_array, v_line, 5)
    f = poly1d(p)
    fiting_line = f(position_r_array)
    new_array[:,n] = fiting_line
velocity_array = new_array

#采用对速度场进行高斯滤波的方法
from scipy.ndimage import gaussian_filter
conv_result = gaussian_filter(velocity_array, sigma = 1)
velocity_array = conv_result


#============================================================
#直接从得到的速度时间序列计算v_eff
#这个方法可以真正意义上获得实时的粘度结果
#如果有什么好的方法去消除噪声就好了，可以使用傅里叶变换，或者函数拟合的方法，后续研究

#求du/dt
#输入velocity_array和time_array和position_r_array，输出dudt_array
dudt_array = np.zeros((len(position_r_array),len(time_array)))
for r in range(len(position_r_array)):
    dudt_array[r,0] = np.polyfit(time_array[0:2],velocity_array[r,0:2],1)[0]
    dudt_array[r,1] = np.polyfit(time_array[0:3],velocity_array[r,0:3],1)[0]
    dudt_array[r,-2] = np.polyfit(time_array[-3:len(time_array)],velocity_array[r,-3:len(time_array)],1)[0]
    dudt_array[r,-1] = np.polyfit(time_array[-2:len(time_array)],velocity_array[r,-2:len(time_array)],1)[0]
    for t in range(2,len(time_array)-2):
        dudt_array[r,t] = np.polyfit(time_array[t-2:t+3],velocity_array[r,t-2:t+3],1)[0]
print('du/dt计算完成')
        
#求du/dr
#输入velocity_array和position_r_array和time_array，输出dudr_array
dudr_array = np.zeros((len(position_r_array),len(time_array)))
for t in range(len(time_array)):
   dudr_array[0,t] = np.polyfit(position_r_array[0:2],velocity_array[0:2,t],1)[0]
   dudr_array[1,t] = np.polyfit(position_r_array[0:3],velocity_array[0:3,t],1)[0]
   dudr_array[-2,t] = np.polyfit(position_r_array[-3:len(position_r_array)],velocity_array[-3:len(position_r_array),t],1)[0]
   dudr_array[-1,t] = np.polyfit(position_r_array[-2:len(position_r_array)],velocity_array[-2:len(position_r_array),t],1)[0]
   for r in range(2,len(position_r_array)-2):
       dudr_array[r,t] = np.polyfit(position_r_array[r-2:r+3],velocity_array[r-2:r+3,t],1)[0]
print('du/dr计算完成')

#求d2u/dr2
#输入velocity_array和position_r_array和time_array，输出d2udr2_array
d2udr2_array = np.zeros((len(position_r_array),len(time_array)))
for t in range(len(time_array)):
   d2udr2_array[0,t] = np.polyfit(position_r_array[0:2],dudr_array[0:2,t],1)[0]
   d2udr2_array[1,t] = np.polyfit(position_r_array[0:3],dudr_array[0:3,t],1)[0]
   d2udr2_array[-2,t] = np.polyfit(position_r_array[-3:len(position_r_array)],dudr_array[-3:len(position_r_array),t],1)[0]
   d2udr2_array[-1,t] = np.polyfit(position_r_array[-2:len(position_r_array)],dudr_array[-2:len(position_r_array),t],1)[0]
   for r in range(2,len(position_r_array)-2):
       d2udr2_array[r,t] = np.polyfit(position_r_array[r-2:r+3],dudr_array[r-2:r+3,t],1)[0]
print('du2/dr2计算完成')

'''
conv_result = gaussian_filter(dudt_array, sigma = 1)
dudt_array = conv_result
conv_result = gaussian_filter(dudr_array, sigma = 1)
dudr_array = conv_result
conv_result = gaussian_filter(d2udr2_array, sigma = 1)
d2udr2_array = conv_result
'''

#求v_eff
#根据公式du/dt=v_eff(d2u/dr2+1/r*du/dr+u/r2)
#输入dudt_array,dudr_array,d2udr2_array,velocity_array,输出v_eff_array
v_eff_array = np.zeros((len(position_r_array),len(time_array)))
for r in range(len(position_r_array)):
    for t in range(len(time_array)):
        A = dudr_array[r,t]/position_r_array[r]
        B = velocity_array[r,t]/(position_r_array[r]*position_r_array[r])
        C = d2udr2_array[r,t]+A+B
        v_eff_array[r,t] = dudt_array[r,t]/C




#==================================================================================
#取t=0~200数据进行三角函数拟合
n = 200
#数据拟合sin曲线降噪
def sin_fit(x,A,B,C):
    return A*np.sin(B*x+C)
p0 = [np.max(velocity_array[0,0:n]),0.5*2*np.pi,1]

p,pc = optimize.curve_fit(sin_fit,time_array[0:n],velocity_array[0,0:n],p0 = p0)

y = p[0]*np.sin(p[1]*time_array[0:n]+p[2])




'''
plt.figure()
plt.scatter(time_array[0:n],velocity_array[0,0:n],color='green')
plt.plot(time_array[0:n],y,color = 'red')
plt.show()
'''





plt.figure()
plt.contourf(time_array[0:200],position_r_array,v_eff_array[:,0:200],range(500,1500,10))
plt.show()


aug = np.mean(v_eff_array)

'''
plt.figure()
plt.plot(position_r_array,v_eff_array[:,0])
plt.contourf(time_array[0:200],position_r_array,v_eff_array[:,0:200])
norml = mpl.colors.Normalize(vmin=150,vmax=250)
iml = mpl.cm.ScalarMappable(norm = norml)
plt.colorbar(iml)

'''


