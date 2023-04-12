import numpy as np
from scipy.special import jv
from pyuvp import Tools

ON = 1
OFF = 0


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
    def __init__(self, datas=None, tdx_num=0, vel_data=None, time_series=None, coordinate_series=None):
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
        self.__cylinder_r = None
        self.__delta_y = None

        self.__shear_rate = None
        self.__viscosity = None

    # Update the variable self.__coordinate_series and self.__vel_data,
    # to store the data in the radial coordinate system.
    # If you don't execute these two functions, the variable will store the coordinates in the xi coordinate system.
    # Running this function will modify the data in self.__coordinate_series and self.__vel_data,
    # to represent the coordinates in the radial coordinate system.
    def settingOuterCylinder(self, cylinder_r, wall_coordinates_in_xi, delta_y):
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

    def extract_analyzable_data(self, extract_range=[0, -1]):
        for i in range(self.__number_of_windows):
            self.__analyzable_vel_data[i] = self.__analyzable_vel_data[i][:, extract_range[0]:extract_range[1]]
        self.__coordinate_series = self.__coordinate_series[extract_range[0]:extract_range[1]]

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
    def do_fft(self, window_num=0, derivative_smoother_factor=[11, 1]):
        my_axis = 0
        N = len(self.__time_series[window_num])
        Delta_T = (self.__time_series[window_num][-1] - self.__time_series[window_num][0]) / N
        fft_result = np.fft.rfft(self.__analyzable_vel_data[window_num], axis=my_axis)
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

    # Calculate effective shear rate, contains the section that do the FFT.
    def calculate_effective_shear_rate(self, window_num=0):
        _, _, _, _, real_part, imag_part = self.do_fft(window_num=window_num)
        real_part_derivative = Tools.derivative(real_part, self.__coordinate_series)
        imag_part_derivative = Tools.derivative(imag_part, self.__coordinate_series)
        param_1 = real_part_derivative - (real_part / self.__coordinate_series)
        param_2 = imag_part_derivative - (imag_part / self.__coordinate_series)
        self.__shear_rate = np.sqrt(param_1 ** 2 + param_2 ** 2)
        return self.__shear_rate

    def calculate_viscosity(self, max_viscosity=30000, viscoity_range_tolerance=1):
        viscosity = []
        shear_rate = []
        for window in range(self.__number_of_windows):
            vibration_frequency, _, _, phase_delay_derivative, real_part, imag_part = self.do_fft(window_num=window)
            # Calculate effective shear rate.
            real_part_derivative = Tools.derivative(real_part, self.__coordinate_series)
            imag_part_derivative = Tools.derivative(imag_part, self.__coordinate_series)
            param_1 = real_part_derivative - (real_part / self.__coordinate_series)
            param_2 = imag_part_derivative - (imag_part / self.__coordinate_series)
            shear_rate.extend(np.sqrt(param_1 ** 2 + param_2 ** 2))

            # Calculate effective viscosity.
            print("\033[1mCalculation Start:")
            print('------------------------------------------------------')
            print('Window_num\t|\tcoordinate_index\t|\tViscosity\033[0m')
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
                        print("\033[1m\033[31mCALCULATION ERROR：\033[0mThe sought viscosity value is out of range.")
                        print('\033[1m------------------------------------------------------')
                        print('Window_num\t|\tcoordinate_index\t|\tViscosity\033[0m')
                        viscosity.append(-1)
                        visc_limits = [0.5, max_viscosity]
                        break
                    if np.abs(temp[0]-temp[1]) < viscoity_range_tolerance:
                        print('\t' + str(window) + '\t\t\033[1m|\033[0m\t\t\t' + str(coordinate_index) +
                              '\t\t\t\033[1m|\033[0m\t' + str(middle_viscosity))
                        viscosity.append(middle_viscosity)
                        visc_limits = [middle_viscosity - visc_range if middle_viscosity - visc_range > 0 else 0.5,
                                       middle_viscosity + visc_range]
                        break
                    else:
                        visc_limits = temp
                        middle_viscosity = (visc_limits[1] + visc_limits[0]) / 2
        self.__shear_rate = np.array(shear_rate)
        self.__viscosity = np.array(viscosity)
        print('\033[1m------------------------------------------------------')
        print("Calculation Complete.\033[0m")
        return self.__shear_rate, self.__viscosity

    def velTableTheta(self, window_num=0):
        return self.__analyzable_vel_data[window_num]

    def timeSlice(self, window_num=0):
        return self.__time_series[window_num]

    def coordinatesR(self, window_num=0):
        window_num = window_num
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

