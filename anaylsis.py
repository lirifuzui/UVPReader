import pandas as pd
import numpy as np
from scipy.signal import savgol_filter
from functools import reduce
from scipy.special import jv

import matplotlib.pyplot as plt

# ======================================
# ||
analysis_shift = 0  # ||
# ||
# ======================================

cylinder_r = 72.5
Delta_y = 16
file_data = pd.read_csv(r'C:\Users\ZHENG WENQING\Desktop\UVPReader\0.5hz120deg-svel.csv')
wall_coordinate = 72.5

smooth_level = [7, 1]

# ===========================================================
# 提取时间序列
time_series = np.array(file_data['time'].values.tolist())
nProfiles = len(list(time_series))
sampleTimes = (time_series[-1] - time_series[0]) / nProfiles
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
xi_wall_to_center = np.sqrt(cylinder_r ** 2 - Delta_y ** 2)  # 计算测量线在圆筒内总长的一半
position_r_list = [np.sqrt((xi_wall_to_center - abs(wall_coordinate - position_xi_list[i])) ** 2 + Delta_y ** 2) for
                   i in range(len(position_xi_list))]  # 计算数据点对应的半径位置，需要给出圆筒壁面坐标
# 输出array形式的采样坐标和时空速度分布
position_r_array = np.array(position_r_list)
velocity_array = np.array(velocity_list)

# 计算速度序列的傅里叶变换
my_axis = 1
FFT_vel = np.fft.rfft(velocity_array, axis=my_axis)
magnitude = np.abs(FFT_vel) / nProfiles
max_magnitude_indices = np.argmax(magnitude, axis=my_axis)
phase_dalay = np.angle(FFT_vel[range(FFT_vel.shape[0]), max_magnitude_indices])
real_part = FFT_vel[range(FFT_vel.shape[0]), max_magnitude_indices].real / nProfiles
imag_part = FFT_vel[range(FFT_vel.shape[0]), max_magnitude_indices].imag / nProfiles

phase_dalay_deriv = np.gradient(phase_dalay, position_r_array)
phase_dalay_deriv_smooth = savgol_filter(phase_dalay_deriv, window_length=smooth_level[0], polyorder=smooth_level[1])
realpart_deriv = np.gradient(real_part, position_r_array)
imagpart_deriv = np.gradient(imag_part, position_r_array)

# 计算剪切率
formula_1 = realpart_deriv - (real_part / position_r_array)
formula_2 = imagpart_deriv - (imag_part / position_r_array)
ShearRate = np.sqrt(formula_1 ** 2 + formula_2 ** 2)

# ------------------------------------------------------
plt.figure()
plt.ylabel(r'$ \phi(r)[\pi] $')
plt.xlabel(r'r/R')
plt.grid()
plt.plot(position_r_array / cylinder_r, (phase_dalay - phase_dalay[0]) * 180 / np.pi)
plt.show()

plt.ylabel(r'$\frac{\mathrm{data} \phi}{\mathrm{data} r} $ ')
plt.xlabel(r'r/R')
plt.grid()
plt.plot(position_r_array / cylinder_r, phase_dalay_deriv_smooth)
plt.show()

Rang = 300
plt.xlabel('t [s]')
plt.ylabel('r/R')
plt.contourf(time_series[0:Rang], position_r_array / cylinder_r, velocity_array[:, 0:Rang])
plt.show()
# ------------------------------------------------------

if analysis_shift:
    None
