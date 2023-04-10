import numpy as np
from scipy.special import jv
import Tools


def Alpha_Bessel(cylinder_R, freq_0, visc, position_array):
    k = np.sqrt(np.pi * freq_0 / visc)
    Beta = (-1 + 1j) * k
    Xi_R = Beta * cylinder_R
    Bessel_R = jv(1, Xi_R)
    Phi_R, Psi_R = np.real(Bessel_R), np.imag(Bessel_R)
    Xi_r = Beta * position_array
    Bessel_r = jv(1, Xi_r)
    Phi_r, Psi_r = np.real(Bessel_r), np.imag(Bessel_r)
    alphas = np.arctan2(Phi_r * Psi_R - Phi_R * Psi_r, Phi_r * Phi_r + Psi_r * Psi_r)
    alphas = np.unwrap(alphas)
    return alphas


cylinder_R: float = 72.5  # 定义圆柱形容器的尺寸
freq_0: float = 1  # 定义容器转动频率
initial_visc = [1, 5, 100]  # 定义粘度的初值和猜测范围
prec = 1  # 定义如果粘度预测范围的最大值和最小值的差小于此值的时候退出
derivative_smoother_factor = [7,1]


def unnamed(phase_delay_derivative, coordinate_series):
    # 自动化计算不同位置的粘度，采用二分法逼近的算法，计算量极高
    result_visc = []
    for i in range(len(coordinate_series)):
        # 遍历可以求导的位置点
        copy_initial_visc = initial_visc.copy()
        for cycle_index in range(50):
            # 定义最大的迭代次数，如果迭代次数超过50，自动退出
            print('在' + str(i) + '点循环' + str(cycle_index + 1) + '次，此时v_eff=' + str(copy_initial_visc[1]))
            # 采用二分法逼近最终值
            predicted_value = []
            for visc in initial_visc:
                alpha = Alpha_Bessel(cylinder_R, freq_0, visc, coordinate_series)
                alpha -= alpha[0]
                alpha = np.abs(alpha)
                alpha_derivative = Tools.derivative(alpha, coordinate_series, derivative_smoother_factor)[i]
                predicted_value.append(alpha_derivative)
            if (predicted_value[0] - phase_delay_derivative[i]) * (
                    phase_delay_derivative[i] - predicted_value[1]) > 0:  # 如果值在预定的粘度最小值和粘度当前值之前
                if abs(copy_initial_visc[0] - copy_initial_visc[2]) < prec:
                    # 判断是否收敛
                    print('在第' + str(i) + '点收敛\n============================================')
                    break
                else:
                    print('标准值:' + str(phase_delay_derivative))
                    print('当前判断值:' + str(predicted_value))
                    initial_visc[2] = copy_initial_visc[1]
                    initial_visc[1] = (copy_initial_visc[0] + copy_initial_visc[1]) / 2
            elif (predicted_value[1] - phase_delay_derivative) * (
                    phase_delay_derivative - predicted_value[2]) > 0:  # 如果值在预定的粘度当前值和粘度最大值值之前
                if abs(copy_initial_visc[0] - copy_initial_visc[2]) < prec:
                    # 判断是否收敛
                    print('在第' + str(i) + '点收敛\n============================================')
                    break
                else:
                    print('标准值:' + str(phase_delay_derivative))
                    print('当前判断值:' + str(predicted_value))
                    copy_initial_visc[0] = copy_initial_visc[1]
                    copy_initial_visc[1] = (copy_initial_visc[1] + copy_initial_visc[2]) / 2
            else:
                print('在第' + str(i) + '点出错\n==============================================')
                print(predicted_value)
                print(phase_delay_derivative)
                print(copy_initial_visc)
                copy_initial_visc[1] = -1
                break
        result_visc.append(copy_initial_visc[1])





