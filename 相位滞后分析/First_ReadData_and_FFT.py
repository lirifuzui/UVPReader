import pandas as pd
import numpy as np
from scipy import fft
import matplotlib.pyplot as plt


#=================================重点参数=========================================
#time_array,采样时间序列;N,采样数;Delta_T,采样时间间隔(平均)
#velocity_list:[array],每个元素是表示某一固定采样点的时间速度序列;velocity_fit_array,时空二维速度序列
#Amp_list:[array],
#FFT_Freq_list:[array],
#AmpMax_array,不同位置的最大振幅
#ArgDelay_array,不同半径处的相位滞后; ArgDelay_fit_array,多项式拟合后的相位滞后函数; ArgDelay_deriv_array,相位滞后函数的导数
#position_r_array,空间采样点序列
#==================================================================================


#定义容器尺寸
cylinder_r :float = 72.5
#定于测量线的位置
Delta_y : float = 16

#===========================================================
#读取文件
#一定注意可以正确读取的文件的书写格式
data :pd.DataFrame = pd.read_csv(r'C:\Users\ZHENG WENQING\Desktop\u_xi500cSt1Hz90deg_vel.csv')
# data :pd.DataFrame = pd.read_csv(r'E:\u盘备份\0.5hz120deg-svel.csv')

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
position_xi_list :float = []
for c in columns:
    if c == 'time': continue
    position_xi_list.append(float(c)) #记录采样坐标
    d = data[c].values.tolist()
    velocity_list.append(np.array([i*float(c)/Delta_y for i in d]))

#将位置坐标转换为半径位置坐标
xi_wall_to_center :float = np.sqrt(cylinder_r**2 - Delta_y**2)
position_r_list = [np.sqrt((xi_wall_to_center-abs(position_xi_list[0]-position_xi_list[i]))**2 + Delta_y**2) for i in range(len(position_xi_list))]
#输出array形式的采样坐标和时空速度分布
position_r_array :np.ndarray = np.array(position_r_list)
velocity_array :np.ndarray = np.array(velocity_list)


def _PhaseDelay_Continuity(front_data,target_data):
    for times in range(10):
        if abs(front_data-target_data)>np.pi/4:
            target_data = target_data + np.pi if target_data<front_data else target_data - np.pi
        else:
            break
    return target_data

            
   
#===========================================================
#计算速度序列的傅里叶变换
FFT_vel_list :[np.ndarray] = []
FFT_Freq_list = [] #傅里叶变换后的频率轴，绘图用
Amp_list :[np.ndarray]= []
AmpMax_list :float = []
ArgDelay_list :float = []
Velreal_list :float = []
Velimag_list :float = []
FFT_times :int = 1
for vel in velocity_list: 
    #对某一位置点的时间速度序列做FFT
    FFT_vel= np.array(fft.fft(vel)[:int(N/2)])
    #计算某一位置点的幅频特性
    Vel_Amp = np.abs(FFT_vel)/N
    #计算最大幅值
    Amp_max :float = float(np.max(Vel_Amp))
    #确定最大幅值频率
    n :int = int(np.where(Vel_Amp==Amp_max)[0][0])
    
    #计算特征相位
    Vel_Arg :float = np.angle(FFT_vel[n])
    #计算频率轴坐标
    freq = np.array(fft.fftfreq(N,Delta_T)[:int(N/2)])
    
    
    #记录结果
    FFT_vel_list.append(FFT_vel) #记录不同位置点速度时间序列傅里叶变换后的列表
    FFT_Freq_list.append(freq) #记录不同位置点的速度傅里叶变换后的频率轴
    Amp_list.append(Vel_Amp) #记录不同位置点的幅频特性，频率的函数
    
    #记录速度的实部和虚部，用于计算实效剪切速率
    Velreal_list.append(FFT_vel[n].real/N)
    Velimag_list.append(FFT_vel[n].imag/N)
    
    AmpMax_list.append(Amp_max) #记录不同位置点的最大幅频特征的列表，位置的函数
    ArgDelay_list.append(Vel_Arg if len(ArgDelay_list) == 0 else _PhaseDelay_Continuity(ArgDelay_list[-1],Vel_Arg)) #记录不同位置点的相位延迟特征的列表，位置的函数
    print('\r傅里叶变换完成：'+str(FFT_times/(len(velocity_list)+1)*100)+'%',end = "")
    FFT_times = FFT_times + 1

#将最大幅值和相位差的转换为array形式
AmpMax_array :np.ndarray = np.array(AmpMax_list)
ArgDelay_array :np.ndarray = np.array(ArgDelay_list)


'''
#===========================================================
#输出相位滞后函数的导数序列ArgDelay_deriv_array，5点一线
def deriv_of_func(array_y,array_x):
    #计算并输出函数的导数序列
    deriv_list = []
    for i in range(2,len(array_x)-2):
        Temp_array_y = array_y[i-2:i+3]
        Temp_array_x = array_x[i-2:i+3]
        formula_1 = sum([( Temp_array_y[j]-np.mean( Temp_array_y))*(Temp_array_x[j]-np.mean(Temp_array_x)) for j in range(5)])
        formula_2 = sum([(Temp_array_x[j]-np.mean(Temp_array_x))**2 for j in range(5)])
        deriv_list.append(formula_1/formula_2)
    array_x_for_deriv_y_array = array_x[2:-2]
    return np.array(deriv_list),array_x_for_deriv_y_array

ArgDelay_deriv,position_r_for_ArgDelay_array = deriv_of_func(ArgDelay_array,position_r_array)
'''


#===========================================================
#输出相位滞后函数的导数序列ArgDelay_deriv_array，7点一线
def deriv_of_func(array_y,array_x):
    #计算并输出函数的导数序列
    deriv_list = []
    for i in range(3,len(array_x)-3):
        Temp_array_y = array_y[i-3:i+4]
        Temp_array_x = array_x[i-3:i+4]
        formula_1 = sum([( Temp_array_y[j]-np.mean( Temp_array_y))*(Temp_array_x[j]-np.mean(Temp_array_x)) for j in range(7)])
        formula_2 = sum([(Temp_array_x[j]-np.mean(Temp_array_x))**2 for j in range(7)])
        deriv_list.append(formula_1/formula_2)
    array_x_for_deriv_y_array = array_x[3:-3]
    return np.array(deriv_list),array_x_for_deriv_y_array

ArgDelay_deriv,position_r_for_ArgDelay_array = deriv_of_func(ArgDelay_array,position_r_array)

#计算实效剪切速率
deriv_of_real,position_r_for_ShearRate_array = deriv_of_func(Velreal_list,position_r_array)
deriv_of_imag = deriv_of_func(Velimag_list,position_r_array)[0]

ShearRate_list :float = []
for i in range(len(position_r_for_ShearRate_array)):
    formula_1 = deriv_of_real[i]-(Velreal_list[3+i]/position_r_for_ShearRate_array[i])
    formula_2 = deriv_of_imag[i]-(Velimag_list[3+i]/position_r_for_ShearRate_array[i])
    ShearRate = np.sqrt(formula_1**2 + formula_2**2)
    ShearRate_list.append(ShearRate)
ShearRate_array = np.array(ShearRate_list)





#||=========================================================================================================||
#||=====                                                                                            ========||
#||=====                                   以下为需要自定义更改的部分                                 ========||
#||=====                                                                                            ========||
#||=========================================================================================================||


#===========================================================
#调整归零相位差曲线，为了画图好看，不影响结果
#这一步需要让壁面附近的相位延迟为0，同时最好让相位延迟都是正数
#这一步最好附加GUI，让用户自己调整
ArgDelay_Wall :float = ArgDelay_list[0]
Temp = ArgDelay_array
ArgDelay_array = np.array([i-ArgDelay_Wall for i in Temp])

'''
#===========================================================
#对上面获得的相位延迟(r)做函数拟合，并求导
#未来这里需要做扩展，直接做成对应不同函数的拟合程序然后嵌入到这里
p5 = np.polyfit(position_r_array,ArgDelay_array,5) #采用9次多项式拟合，p9为从高次到低次的多项式系数的
f5 = np.poly1d(p5) # 组合乘多项式函数
f5_deriv = f5.deriv() #对上式求导数

#||=========================================================================================================||
#||=====                                                                                            ========||
#||=====                                   以上为需要自定义更改的部分                                 ========||
#||=====                                                                                            ========||
#||=========================================================================================================||

#=====================最终目标==============================
#获得拟合序列和导数序列
ArgDelay_fit_array = f5(position_r_array)
ArgDelay_deriv = f5_deriv(position_r_array[1:-1])
position_r_for_ArgDelay_array = position_r_array[1:-1]
'''

#=============================计算剪切速率====================================
#============================================================================





#==================输出相位滞后位置函数图像====================================
#============================================================================
plt.figure()
plt.xlabel(r'$ \phi(r)[\pi] $')
plt.ylabel(r'r/R')
plt.grid ()
plt.plot(ArgDelay_array*180/np.pi,position_r_array/cylinder_r)
plt.show()
#============================================================================
#============================================================================



#==================输出相位滞后位置函数的导数图像==============================
#============================================================================
plt.figure()
plt.xlabel(r'$\frac{\mathrm{d} \phi}{\mathrm{d} r} $ ')
plt.ylabel(r'r/R')
plt.grid ()
plt.plot(ArgDelay_deriv,position_r_for_ArgDelay_array/cylinder_r)
plt.show()
#============================================================================
#============================================================================



#==================输出时空速度云图===========================================
#============================================================================
Rang = 100
plt.figure()
plt.xlabel('t [s]')
plt.ylabel('r/R')
plt.contourf(time_array[0:Rang],position_r_array/cylinder_r,velocity_array [:,0:Rang])
plt.show()
#============================================================================
#============================================================================






    
    
    





