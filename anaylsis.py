import pandas as pd
import numpy as np
from scipy import fft
import matplotlib.pyplot as plt

cylinder_r = 72.5
Delta_y = 16
file_data = pd.read_csv(r'C:\Work file\Now_Pros\UVPReader\u_xi500cSt1Hz90deg_vel.csv')
wall_coordinate = 0

# ===========================================================
# 提取时间序列
time_series = np.array(file_data['time'].values.tolist())
nProfiles = len(list(time_series))
Delta_T = (time_series[-1] - time_series[0]) / nProfiles
# ===========================================================
# 提取并计算圆周速度序列
velocity_list = []
lines = file_data.columns
position_xi_list = []
for line in lines:
    if line == 'time':
        continue
    position_xi_list.append(float(line))  # 记录采样坐标
    data = file_data[line].values.tolist()
    velocity_list.append(np.array([i * float(line) / Delta_y for i in data]))

# 将位置坐标转换为半径位置坐标
xi_wall_to_center = np.sqrt(cylinder_r ** 2 - Delta_y ** 2) # 计算测量线在圆筒内总长的一半
position_r_list = [np.sqrt((xi_wall_to_center - abs(wall_coordinate - position_xi_list[i])) ** 2 + Delta_y ** 2) for
                   i in range(len(position_xi_list))] # 计算数据点对应的半径位置，需要给出圆筒壁面坐标
# 输出array形式的采样坐标和时空速度分布
position_r_array = np.array(position_r_list)
velocity_array = np.array(velocity_list)


def _PhaseDelay_Continuity(front_data, target_data):
    for times in range(10):
        if abs(front_data - target_data) > np.pi / 4:
            target_data = target_data + np.pi if target_data < front_data else target_data - np.pi
        else:
            break
    return target_data


# ===========================================================
# 计算速度序列的傅里叶变换
AmpMax_list = []
ArgDelay_list = []
Velreal_list = []
Velimag_list = []
FFT_times = 1
for vel in velocity_list:
    # 对某一位置点的时间速度序列做FFT
    FFT_vel = np.fft.rfft(vel)
    # 计算某一位置点的幅频特性
    Vel_Amp = np.abs(FFT_vel) / nProfiles
    # 找到最大幅值和对应的频率
    Amp_max, n = np.max(Vel_Amp), np.argmax(Vel_Amp)
    # 计算特征相位
    Vel_Arg = np.angle(FFT_vel[n])
    # 记录速度的实部和虚部，用于计算实效剪切速率
    Velreal_list.append(FFT_vel[n].real / nProfiles)
    Velimag_list.append(FFT_vel[n].imag / nProfiles)

    AmpMax_list.append(Amp_max)  # 记录不同位置点的最大幅频特征的列表，位置的函数
    ArgDelay_list.append(Vel_Arg if len(ArgDelay_list) == 0 else _PhaseDelay_Continuity(ArgDelay_list[-1],Vel_Arg))  # 记录不同位置点的相位延迟特征的列表，位置的函数
    print('\r傅里叶变换完成：' + str(FFT_times / (len(velocity_list) + 1) * 100) + '%', end="")
    FFT_times = FFT_times + 1
# 将最大幅值和相位差的转换为array形式
AmpMax_array: np.ndarray = np.array(AmpMax_list)
ArgDelay_array: np.ndarray = np.array(ArgDelay_list)



# ===========================================================
# 输出相位滞后函数的导数序列ArgDelay_deriv_array，7点一线
def calculate_derivative(array_y, array_x, window_size=7):
    deriv_list = []
    avg_y = np.mean(array_y)
    avg_x = np.mean(array_x)
    for i in range(window_size // 2, len(array_x) - window_size // 2):
        temp_array_y = array_y[i - window_size // 2:i + window_size // 2 + 1]
        temp_array_x = array_x[i - window_size // 2:i + window_size // 2 + 1]
        formula_1 = np.dot(temp_array_y - avg_y, temp_array_x - avg_x)
        formula_2 = np.dot(temp_array_x - avg_x, temp_array_x - avg_x)
        deriv_list.append(formula_1 / formula_2)
    return np.array(deriv_list), array_x[window_size//2:-window_size//2]


ArgDelay_deriv, position_r_for_ArgDelay_array = calculate_derivative(ArgDelay_array, position_r_array,7)

# 计算实效剪切速率
deriv_of_real, position_r_for_ShearRate_array = calculate_derivative(Velreal_list, position_r_array,7)
deriv_of_imag = calculate_derivative(Velimag_list, position_r_array,7)[0]

ShearRate_list: float = []
for i in range(len(position_r_for_ShearRate_array)):
    formula_1 = deriv_of_real[i] - (Velreal_list[3 + i] / position_r_for_ShearRate_array[i])
    formula_2 = deriv_of_imag[i] - (Velimag_list[3 + i] / position_r_for_ShearRate_array[i])
    ShearRate = np.sqrt(formula_1 ** 2 + formula_2 ** 2)
    ShearRate_list.append(ShearRate)
ShearRate_array = np.array(ShearRate_list)

# ||=========================================================================================================||
# ||=====                                                                                            ========||
# ||=====                                   以下为需要自定义更改的部分                                 ========||
# ||=====                                                                                            ========||
# ||=========================================================================================================||


# ===========================================================
# 调整归零相位差曲线，为了画图好看，不影响结果
# 这一步需要让壁面附近的相位延迟为0，同时最好让相位延迟都是正数
# 这一步最好附加GUI，让用户自己调整
ArgDelay_Wall: float = ArgDelay_list[0]
Temp = ArgDelay_array
ArgDelay_array = np.array([i - ArgDelay_Wall for i in Temp])

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

# =============================计算剪切速率====================================
# ============================================================================


# ==================输出相位滞后位置函数图像====================================
# ============================================================================
plt.figure()
plt.xlabel(r'$ \phi(r)[\pi] $')
plt.ylabel(r'r/R')
plt.grid()
plt.plot(ArgDelay_array * 180 / np.pi, position_r_array / cylinder_r)
plt.show()
# ============================================================================
# ============================================================================


# ==================输出相位滞后位置函数的导数图像==============================
# ============================================================================
plt.figure()
plt.xlabel(r'$\frac{\mathrm{data} \phi}{\mathrm{data} r} $ ')
plt.ylabel(r'r/R')
plt.grid()
plt.plot(ArgDelay_deriv, position_r_for_ArgDelay_array / cylinder_r)
plt.show()
# ============================================================================
# ============================================================================


# ==================输出时空速度云图===========================================
# ============================================================================
Rang = 100
plt.figure()
plt.xlabel('t [s]')
plt.ylabel('r/R')
plt.contourf(time_series[0:Rang], position_r_array / cylinder_r, velocity_array[:, 0:Rang])
plt.show()
# ============================================================================
# ============================================================================














