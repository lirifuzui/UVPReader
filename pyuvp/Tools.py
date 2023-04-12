import numpy as np
from scipy.signal import savgol_filter

ON = 1
OFF = 0


def moving_average(data, window_size, axis=0):
    weights = np.repeat(1.0, window_size) / window_size
    return np.apply_along_axis(lambda m: np.convolve(m, weights, 'valid'), axis=axis, arr=data)


def moving_var(data, window_size, axis=0):
    weights = np.ones(window_size) / window_size
    mean = np.apply_along_axis(lambda m: np.convolve(m, weights, 'valid'), axis=axis, arr=data)
    square_mean = np.apply_along_axis(lambda m: np.convolve(m ** 2, weights, 'valid'), axis=axis, arr=data)
    var = square_mean - mean ** 2
    return var


def moving_std(data, window_size, axis=0):
    return np.sqrt(moving_var(data, window_size, axis))


def summary_statistic(data, axis=0):
    mean = np.mean(data, axis=axis)
    std = np.std(data, axis=axis)
    return mean, std


def derivative(array_y, array_x, derivative_smoother_factor=OFF):
    dy_dx = np.gradient(array_y, array_x)
    if derivative_smoother_factor == OFF:
        return dy_dx
    else:
        dy_dx_smooth = savgol_filter(dy_dx, window_length=derivative_smoother_factor[0],
                                     polyorder=derivative_smoother_factor[1])
        return dy_dx_smooth
