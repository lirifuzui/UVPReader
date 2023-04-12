import numpy as np
from scipy.special import jv
import Tools


def phase_unwrap(alphas):
    dphase = np.diff(alphas)
    idx1 = np.where(dphase > np.pi / 2)[0]
    idx2 = np.where(dphase < -np.pi / 2)[0]
    print(idx1, idx2)
    offsets = np.zeros_like(alphas)
    for p in idx1:
        offsets[p + 1:] -= np.pi
    for p in idx2:
        offsets[p + 1:] += np.pi
    alphas += offsets
    return alphas


def Alpha_Bessel(cylinder_R, freq_0, visc, coordinates_r):
    Beta = np.sqrt(-1j * 2 * np.pi * freq_0 / visc)
    Xi_R = Beta * cylinder_R
    Bessel_R = jv(1, Xi_R)
    Phi_R, Psi_R = np.real(Bessel_R), np.imag(Bessel_R)
    Xi_r = Beta * coordinates_r
    Bessel_r = jv(1, Xi_r)
    Phi_r, Psi_r = np.real(Bessel_r), np.imag(Bessel_r)
    alphas = np.arctan(((Phi_r * Psi_R) - (Phi_R * Psi_r)) / ((Phi_r * Phi_R) + (Psi_r * Psi_R)))
    dphase = np.diff(alphas)
    offsets = np.zeros_like(alphas)
    for idx, p in enumerate(dphase):
        if p > np.pi / 2:
            offsets[idx + 1:] -= np.pi
        elif p < -np.pi / 2:
            offsets[idx + 1:] += np.pi
    alphas = np.abs(alphas + offsets - alphas[0])
    return alphas


cylinder_R: float = 72.5  # 定义圆柱形容器的尺寸
freq_0: float = 1  # 定义容器转动频率
initial_viscosity = 30000  # 定义粘度的初值和猜测范围
viscoity_range_tolerance = 1  # 定义如果粘度预测范围的最大值和最小值的差小于此值的时候退出


# Automatically calculate the viscosity of different positions,
# using the algorithm of bisection approximation, the calculation amount is extremely high.
def visc_analysis(phase_delay_derivative, coordinate_series, cylinder_R, freq, max_viscosity, viscoity_range_tolerance):
    visc_range = [0, max_viscosity]
    for n in range(len(coordinate_series)):
        loop_count = int(np.log2(visc_range[1]-visc_range[0])) + 1
        for loop in range(loop_count):



viscoity = visc_analysis(None, None, None, None, None, None)
