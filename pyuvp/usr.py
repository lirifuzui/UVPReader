import numpy as np
from scipy.special import jv
import traceback

import pyuvp.uvp
from pyuvp import Tools

ON = 1
OFF = 0


class USRException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{self.message}"


class Statistic:
    def __init__(self, datas=None, tdx_num=0, vel_data=None, echo_data=None):
        self.__vel_data = np.array(datas.vel_table if datas else vel_data)
        self.__echo_data = np.array(datas.echoTables if datas else echo_data)

    # Return the average, maximum, and minimum values of the speed at different positions.
    # The structure is three one-dimensional arrays.
    @property
    def vel_average(self):
        vel_average = np.mean(self.__vel_data, axis=0)
        vel_max = np.max(self.__vel_data, axis=0)
        vel_min = np.min(self.__vel_data, axis=0)
        return vel_average, vel_max, vel_min

    def movvar(self):
        None


class Analysis:
    def __init__(self, datas: pyuvp.uvp.readData = None, tdx_num: int = OFF, vel_data: np.ndarray = None,
                 time_series: np.ndarray = None, coordinate_series: np.ndarray = None):
        # Considering that the speed data will be time-sliced later,
        # self.__vel data and self.__time series are stored in a list,
        # and each item corresponds to a window.
        # self.__analyzable_vel_data and self.__time series should be equal in length.
        # self.__analyzable_vel_data store the pruned analyzable data, and initialize to store the complete data.
        self.__analyzable_vel_data = [datas.velTables(tdx_num) if datas else vel_data(tdx_num)]
        self.__time_series = [datas.timeSeries(tdx_num) if datas else time_series(tdx_num)]
        self.__coordinate_series = datas.coordinateSeries(tdx_num) if datas else coordinate_series(tdx_num)
        # Store the pruned analyzable data, and initialize to store the complete data.
        # number of windows, default 1.
        self.__number_of_windows = 1
        self.__slice = [[0, len(self.__time_series[0])]]
        self.__cylinder_r = None
        self.__delta_y = None

        self.__shear_rate = None
        self.__viscosity = None

    # Update the variable self.__coordinate_series and self.__vel_data,
    # to store the data in the radial coordinate system.
    # If you don't execute these two functions, the variable will store the coordinates in the xi coordinate system.
    # Running this function will modify the data in self.__coordinate_series and self.__vel_data,
    # to represent the coordinates in the radial coordinate system.
    def settingOuterCylinder(self, cylinder_r: int | float, wall_coordinates_in_xi: int | float, delta_y: int | float):
        self.__cylinder_r = cylinder_r
        self.__delta_y = delta_y
        # Update the variable self.__coordinate_series
        half_chord = np.sqrt(cylinder_r ** 2 - delta_y ** 2)
        self.__coordinate_series = np.sqrt((wall_coordinates_in_xi + half_chord -
                                            self.__coordinate_series) ** 2 + delta_y ** 2)
        # Update the variable self.__analyzable_vel_data
        for i in range(self.__number_of_windows):
            self.__analyzable_vel_data[i] = np.multiply(self.__analyzable_vel_data[i], self.__coordinate_series / delta_y)
        return self.__analyzable_vel_data, self.__coordinate_series

    def settingInterCylinder(self, cylinder_r, wall_coordinates_xi, delta_y):
        None

    # Extracted vaild data according to the position coordinates.
    def validVelData(self, start: int = 0, end: int = -1):
        for i in range(self.__number_of_windows):
            self.__analyzable_vel_data[i] = self.__analyzable_vel_data[i][:, start:end]
        self.__coordinate_series = self.__coordinate_series[start:end]

    def slice(self, number_of_slice: int = 5):
        self.__number_of_windows = number_of_slice
        if number_of_slice == 1:
            self.__time_series = [self.__time_series[0]]
            self.__analyzable_vel_data = [self.__analyzable_vel_data[0]]
            self.__slice = [self.__slice[0]]
        elif number_of_slice == 2:
            self.__time_series = [self.__time_series[0],
                                  self.__time_series[0][0:len(self.__time_series[0])//2],
                                  self.__time_series[0][len(self.__time_series[0])//2:-1]]
            self.__analyzable_vel_data = [self.__analyzable_vel_data[0],
                                          self.__analyzable_vel_data[0][0:len(self.__time_series[0])//2, :],
                                          self.__analyzable_vel_data[0][len(self.__time_series[0])//2:-1, :]]
            self.__slice = [self.__slice[0],
                            self.__slice[0][0:len(self.__time_series[0]) // 2],
                            self.__slice[0][len(self.__time_series[0]) // 2:-1]]
        else:
            self.__time_series = [self.__time_series[0]]
            self.__analyzable_vel_data = [self.__analyzable_vel_data[0]]
            self.__slice = [self.__slice[0]]
            moving = len(self.__time_series[0]) // ((number_of_slice-1)*2)
            for slice_index in range(number_of_slice):
                start = 0 + slice_index * moving
                end = -1 - (number_of_slice-1-slice_index)*moving
                self.__time_series.append(self.__time_series[0][start:end])
                self.__analyzable_vel_data.append(self.__analyzable_vel_data[0][start:end, :])
                self.__slice.append([start, end])

    # Unwrapping the phase function.
    def __phase_unwrap(self, phase_delay):
        dphase = np.diff(phase_delay)
        idx1 = np.where(dphase > np.pi)[0]
        idx2 = np.where(dphase < -np.pi)[0]
        offsets = np.zeros_like(phase_delay)
        for p in idx1:
            offsets[p + 1:] -= 2 * np.pi
        for p in idx2:
            offsets[p + 1:] += 2 * np.pi
        phase_delay += offsets
        return phase_delay

    # Compute the phase delay(alpha) via the Bessel function.
    def __Alpha_Bessel(self, cylinder_R, freq_0, visc, coordinates_r):
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

    # do the FFT.
    def doFFT(self, window_num=1, derivative_smoother_factor: int = 11):
        my_axis = 0
        N = len(self.__time_series[window_num-1])
        Delta_T = (self.__time_series[window_num-1][-1] - self.__time_series[window_num-1][0]) / N
        fft_result = np.fft.rfft(self.__analyzable_vel_data[window_num-1], axis=my_axis)
        magnitude = np.abs(fft_result)
        max_magnitude_indices = np.argmax(magnitude, axis=my_axis)
        freq_array = np.fft.fftfreq(N, Delta_T)
        vibration_frequency = np.mean(freq_array[max_magnitude_indices])
        max_magnitude = np.abs(fft_result[max_magnitude_indices, range(fft_result.shape[1])]) / (N/2)
        phase_delay = np.angle(fft_result[max_magnitude_indices, range(fft_result.shape[1])])
        phase_delay = self.__phase_unwrap(phase_delay)
        phase_delay -= phase_delay[0]
        phase_delay = np.abs(phase_delay)
        phase_delay_derivative = Tools.derivative(phase_delay, self.__coordinate_series, derivative_smoother_factor)
        real_part = fft_result[max_magnitude_indices, range(fft_result.shape[1])].real / (N/2)
        imag_part = fft_result[max_magnitude_indices, range(fft_result.shape[1])].imag / (N/2)
        return vibration_frequency, max_magnitude, phase_delay, phase_delay_derivative, real_part, imag_part

    # Calculate Viscosity and Shear Rate.
    def calculate_Viscosity_ShearRate(self, max_viscosity=30000, viscoity_range_tolerance=1,
                                      smooth_level: int = 11):
        viscosity = []
        shear_rate = []
        err_lim = len(self.__coordinate_series) // 5
        # Format the output.
        slice_width = 8
        coordinate_width = 8
        viscosity_width = 20
        shear_rate_width = 20
        print("\033[1mCalculation Start:")
        print('------------------------------------------------------')
        print(f"{'slice':<{slice_width}}{'index':<{coordinate_width}}"
              f"{'Viscosity':<{viscosity_width}}{'shear_rate':<{shear_rate_width}}\033[0m")
        err_time = 0
        err_str = "The sought viscosity value is out of range."
        for window in range(self.__number_of_windows+1):
            vibration_frequency, _, _, phase_delay_derivative, real_part, imag_part = self.doFFT(window_num=window,
                                                                                                 derivative_smoother_factor=smooth_level)
            # Calculate effective shear rate.
            real_part_derivative = Tools.derivative(real_part, self.__coordinate_series)
            imag_part_derivative = Tools.derivative(imag_part, self.__coordinate_series)
            param_1 = real_part_derivative - (real_part / self.__coordinate_series)
            param_2 = imag_part_derivative - (imag_part / self.__coordinate_series)
            shear_rate.extend(np.sqrt(param_1 ** 2 + param_2 ** 2))

            # Calculate effective viscosity.
            visc_limits = [0.5, max_viscosity]
            visc_range = int((max_viscosity - 0.5) / 20)
            for coordinate_index in range(len(self.__coordinate_series)):
                loop_count = int(np.log2(visc_limits[1] - visc_limits[0])) + 10
                middle_viscosity = (visc_limits[1] + visc_limits[0]) / 2
                for loop in range(loop_count):
                    alpha_min = self.__Alpha_Bessel(self.__cylinder_r, vibration_frequency, visc_limits[0],
                                                    self.__coordinate_series)
                    alpha_min_derivative = Tools.derivative(alpha_min, self.__coordinate_series)[coordinate_index]
                    alpha_max = self.__Alpha_Bessel(self.__cylinder_r, vibration_frequency, visc_limits[1],
                                                    self.__coordinate_series)
                    alpha_max_derivative = Tools.derivative(alpha_max, self.__coordinate_series)[coordinate_index]
                    alpha_middle = self.__Alpha_Bessel(self.__cylinder_r, vibration_frequency,
                                                       middle_viscosity, self.__coordinate_series)
                    alpha_middle_derivative = Tools.derivative(alpha_middle, self.__coordinate_series)[coordinate_index]
                    simulate_value = np.array([alpha_min_derivative, alpha_middle_derivative, alpha_max_derivative])
                    idx = np.searchsorted(simulate_value, phase_delay_derivative[coordinate_index])
                    if idx == 1:
                        temp = [visc_limits[0], middle_viscosity]
                    elif idx == 2:
                        temp = [middle_viscosity, visc_limits[1]]
                    else:
                        print("#coordinate_index = " + str(coordinate_index))
                        print("\033[1m\033[31mCALCULATION ERROR：\033[0m" + err_str)
                        print(f"\033[1m{'slice':<{slice_width}}{'index':<{coordinate_width}}"
                              f"{'Viscosity':<{viscosity_width}}{'shear_rate':<{shear_rate_width}}\033[0m")
                        viscosity.append(-1)
                        visc_limits = [0.5, max_viscosity]
                        err_time += 1
                        break
                    if np.abs(temp[0]-temp[1]) < viscoity_range_tolerance:
                        print(f'{str(window):<{slice_width}}{str(coordinate_index):<{coordinate_width}}'
                              f'{middle_viscosity:<{viscosity_width}.7g}'
                              f'{shear_rate[coordinate_index]:<{shear_rate_width}.5g}')
                        viscosity.append(middle_viscosity)
                        visc_limits = [middle_viscosity - visc_range if middle_viscosity - visc_range > 0 else 0.5,
                                       middle_viscosity + visc_range]
                        break
                    else:
                        visc_limits = temp
                        middle_viscosity = (visc_limits[1] + visc_limits[0]) / 2
                if err_time > err_lim:
                    break
            if err_time > err_lim:
                print("\033[1m\033[31mCALCULATION ERROR!!!\033[0m")
                raise USRException(err_str)
                break
        self.__shear_rate = np.array(shear_rate)
        self.__viscosity = np.array(viscosity)
        print('\033[1m------------------------------------------------------')
        print("Calculation Complete.\033[0m")
        return self.__viscosity, self.__shear_rate,

    def velTableTheta(self, window_num=OFF):
        return self.__analyzable_vel_data[window_num]

    def timeSeries(self, window_num=OFF):
        return self.__time_series[window_num]

    @property
    def coordinatesR(self):
        return self.__coordinate_series

    @property
    def geometry(self):
        return self.__cylinder_r, self.__delta_y

    @property
    def shearRate(self):
        return self.__shear_rate

    @property
    def viscosity(self):
        return self.__viscosity

