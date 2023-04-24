import numpy as np
from scipy.special import jv

import pyuvp.uvp
from pyuvp import Tools

ON = 1
OFF = 0


class USRException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{self.message}\n*You should check that:" \
               f"\n*Whether the data file opens correctly." \
               f"\n*Whether the data being analyzed contains some data that no physical meaning." \
               f"\n*Whether the data being analyzed still contains data with large errors." \
               f"\n*Whether the container size is defined correctly."


ExceptionConfig = {
    'Allowable magnification of frequency difference': 0.1,
    'Allowable proportion of calculation error points': 0.3
}


class Statistic:
    def __init__(self, datas=None, tdx_num=0, vel_data=None, echo_data=None):
        self.__vel_data = np.array(datas.velTables(tdx_num) if datas else vel_data(tdx_num))
        self.__echo_data = np.array(datas.echoTables(tdx_num) if datas else echo_data(tdx_num))

    # Return the average, maximum, and minimum values of the speed at different positions.
    # The structure is three one-dimensional arrays.
    @property
    def vel_average(self):
        vel_average = np.mean(self.__vel_data, axis=0)
        vel_max = np.max(self.__vel_data, axis=0)
        vel_min = np.min(self.__vel_data, axis=0)
        return vel_average, vel_max, vel_min

    def echo_average(self):
        echo_average = np.mean(self.__echo_data, axis=0)
        echo_max = np.max(self.__echo_data, axis=0)
        echo_min = np.min(self.__echo_data, axis=0)
        return echo_average, echo_max, echo_min

    def movvar(self):
        None


def geometry(data: pyuvp.uvp.readData, tdx_num: int, cylinder_r: float):
    vel = data.velTables[tdx_num]
    echo = data.echoTable[tdx_num]


class Analysis:
    def __init__(self, datas: pyuvp.uvp.readData = None, tdx_num: int = OFF, vel_data: list = None,
                 time_series: list = None, coordinate_series: list = None, ignoreException=False):
        # Considering that the speed data will be time-sliced later,
        # self.__vel data and self.__time series are stored in a list,
        # and each item corresponds to a window.
        # self.__vel_data and self.__time series should be equal in length.
        # self.__vel_data store the pruned analyzable data, and initialize to store the complete data.
        self.__vel_data: list[np.ndarray] = [datas.velTables[tdx_num] if datas else vel_data[tdx_num]]
        self.__time_series: list[np.ndarray] = [datas.timeSeries[tdx_num] if datas else time_series[tdx_num]]
        self.__coordinate_series: np.ndarray = datas.coordinateSeries[tdx_num] if datas else coordinate_series[tdx_num]

        self.__temp_vel: list[np.ndarray] = [datas.velTables[tdx_num] if datas else vel_data[tdx_num]]
        self.__temp_coords: np.ndarray = datas.coordinateSeries[tdx_num] if datas else coordinate_series[tdx_num]
        # Store the pruned analyzable data, and initialize to store the complete data.
        # number of windows, default 1.
        self.__number_of_windows: int = 1
        self.__slice: list[list[int]] = [[0, len(self.__time_series[0])]]

        self.__cylinder_radius: float | None = None
        self.__delta_y = None

        self.__pipe_TDXangle: float | None = None

        self.__cylinder_freq = None

        self.__shear_rate: np.ndarray | None = None
        self.__viscosity: np.ndarray | None = None

        self.__ignoreUSRException = ignoreException

    # Update the variable self.__coordinate_series and self.__vel_data,
    # to store the data in the radial coordinate system.
    # If you don't execute these two functions, the variable will store the coordinates in the xi coordinate system.
    # Running this function will modify the data in self.__coordinate_series and self.__vel_data,
    # to represent the coordinates in the radial coordinate system.
    def cylinderGeom(self, radius: int | float, wall_coordinate: int | float | None = None,
                     delta_y: int | float | None = None, vibration_params: list[float] | None = None,
                     outward=False, fixedTDX=False, ignoreException=False):
        if delta_y is None and vibration_params is None and wall_coordinate is None:
            raise ValueError("the parameters delta_y, wall_coordinate and vibration_params are required!")
        elif ((delta_y is None and wall_coordinate is not None) or (
                delta_y is not None and wall_coordinate is None)) and vibration_params is None:
            raise ValueError("If you don't use vibration params, both delta_y and wall_coords_xi are required!")

        self.__cylinder_radius = radius
        if delta_y is not None:
            self.__delta_y = delta_y
        else:
            self.__cylinder_freq = vibration_params[0]
            max_vel = 2 * np.pi * self.__cylinder_freq * self.__cylinder_radius * (vibration_params[1] * np.pi / 180)
            self.__vel_data, self.__temp_vel = self.__temp_vel, self.__vel_data
            self.__coordinate_series, self.__temp_coords = self.__temp_coords, self.__coordinate_series
            vibration_frequency, max_magnitude, _, _, _, _ = self.doFFT()
            wall_coordinate = self.__coordinate_series[np.argmax(max_magnitude)]
            self.__coordinate_series, self.__temp_coords = self.__temp_coords, self.__coordinate_series
            self.__vel_data, self.__temp_vel = self.__temp_vel, self.__vel_data
            self.__delta_y = self.__cylinder_radius * np.max(max_magnitude) / max_vel
            if self.__delta_y > self.__cylinder_radius:
                raise ValueError("Delta y is greater than the cylinder radius!")
        # Update the variable self.__coordinate_series
        half_chord = np.sqrt(radius ** 2 - self.__delta_y ** 2)
        self.__coordinate_series = np.sqrt((wall_coordinate + half_chord -
                                            self.__coordinate_series) ** 2 + self.__delta_y ** 2)
        # Update the variable self.__vel_data
        for i in range(self.__number_of_windows):
            self.__vel_data[i] = np.multiply(self.__vel_data[i],
                                             self.__coordinate_series / self.__delta_y)
        return self.__vel_data, self.__coordinate_series

    # Extracted vaild data according to the position coordinates.
    def coordsClean(self, start: int = 0, end: int = -1):
        for i in range(self.__number_of_windows):
            self.__vel_data[i] = self.__vel_data[i][:, start:end]
        self.__coordinate_series = self.__coordinate_series[start:end]

    def timeSlicing(self, number_of_slice: int = 5):
        self.__number_of_windows = number_of_slice
        if number_of_slice == 1 or number_of_slice == 0:
            self.__number_of_windows = 1
            self.__time_series = [self.__time_series[0]]
            self.__vel_data = [self.__vel_data[0]]
            self.__slice = [self.__slice[0]]
        elif number_of_slice == 2:
            self.__time_series = [self.__time_series[0],
                                  self.__time_series[0][:len(self.__time_series[0]) // 2],
                                  self.__time_series[0][len(self.__time_series[0]) // 2:]]
            self.__vel_data = [self.__vel_data[0],
                               self.__vel_data[0][:len(self.__time_series[0]) // 2, :],
                               self.__vel_data[0][len(self.__time_series[0]) // 2:, :]]
            self.__slice = [self.__slice[0],
                            self.__slice[0][:len(self.__time_series[0]) // 2],
                            self.__slice[0][len(self.__time_series[0]) // 2:]]
        else:
            self.__time_series = [self.__time_series[0]]
            self.__vel_data = [self.__vel_data[0]]
            self.__slice = [self.__slice[0]]
            moving = len(self.__time_series[0]) // ((number_of_slice - 1) * 2)
            for slice_index in range(number_of_slice):
                start = 0 + slice_index * moving
                end = -1 - (number_of_slice - 1 - slice_index) * moving
                self.__time_series.append(self.__time_series[0][start:end])
                self.__vel_data.append(self.__vel_data[0][start:end, :])
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
    def doFFT(self, window_num: int = 1, derivative_smoother_factor: int = 11):
        my_axis = 0
        N = len(self.__time_series[window_num - 1])
        Delta_T = (self.__time_series[window_num - 1][-1] - self.__time_series[window_num - 1][0]) / (N - 1)
        fft_result = np.fft.rfft(self.__vel_data[window_num - 1], axis=my_axis)
        magnitude = np.abs(fft_result)
        max_magnitude_indices = np.argmax(magnitude, axis=my_axis)
        freq_array = np.fft.rfftfreq(N, Delta_T)
        vibration_frequency = np.mean(np.abs(freq_array[max_magnitude_indices]))
        max_magnitude = np.abs(fft_result[max_magnitude_indices, range(fft_result.shape[1])]) / (N / 2)
        phase_delay = np.angle(fft_result[max_magnitude_indices, range(fft_result.shape[1])])
        phase_delay = self.__phase_unwrap(phase_delay)
        phase_delay -= phase_delay[0]
        phase_delay = np.abs(phase_delay)
        phase_delay_derivative = Tools.derivative(phase_delay, self.__coordinate_series, derivative_smoother_factor)
        real_part = fft_result[max_magnitude_indices, range(fft_result.shape[1])].real / (N / 2)
        imag_part = fft_result[max_magnitude_indices, range(fft_result.shape[1])].imag / (N / 2)
        return vibration_frequency, max_magnitude, phase_delay, phase_delay_derivative, real_part, imag_part

    # Calculate Viscosity and Shear Rate.
    def calculate_Viscosity_ShearRate(self, max_viscosity: int | float = 30000, viscosity_range_tolerance: int | float = 1,
                                      smooth_level: int = 11, ignoreException=False):
        if self.__cylinder_radius is None and self.__pipe_TDXangle is None:
            raise ValueError("You must define Container Geometry first！")
        viscosity = []
        shear_rate = []
        err_lim = len(self.__coordinate_series) // \
                  (1 / ExceptionConfig['Allowable proportion of calculation error points'])
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
        for window in range(self.__number_of_windows + 1):
            vibration_frequency, _, _, phase_delay_derivative, real_part, imag_part = \
                self.doFFT(window_num=window, derivative_smoother_factor=smooth_level)
            self.__cylinder_freq = vibration_frequency if self.__cylinder_freq == None else self.__cylinder_freq
            if np.abs(vibration_frequency - self.__cylinder_freq) > \
                    np.abs(vibration_frequency * ExceptionConfig['Allowable magnification of frequency difference']) \
                    and not self.__ignoreUSRException and not ignoreException:
                raise USRException("The defined vibration frequency of the cylinder does not match the results of the "
                                   "experimental data! [" + f"{vibration_frequency:.3g}" + ", " + str(
                    self.__cylinder_freq) + "]")
            # Calculate effective shear rate.
            real_part_derivative = Tools.derivative(real_part, self.__coordinate_series)
            imag_part_derivative = Tools.derivative(imag_part, self.__coordinate_series)
            param_1 = real_part_derivative - (real_part / self.__coordinate_series)
            param_2 = imag_part_derivative - (imag_part / self.__coordinate_series)
            shear_rate.extend(np.sqrt(param_1 ** 2 + param_2 ** 2))

            # Calculate effective viscosity.
            viscosity_limits = [0.5, max_viscosity]
            visc_range = int((max_viscosity - 0.5) / 20)
            for coordinate_index in range(len(self.__coordinate_series)):
                loop_count = int(np.log2(viscosity_limits[1] - viscosity_limits[0])) + 10
                middle_viscosity = (viscosity_limits[1] + viscosity_limits[0]) / 2
                for loop in range(loop_count):
                    alpha_min = self.__Alpha_Bessel(self.__cylinder_radius, vibration_frequency, viscosity_limits[0],
                                                    self.__coordinate_series)
                    alpha_min_derivative = Tools.derivative(alpha_min, self.__coordinate_series)[coordinate_index]
                    alpha_max = self.__Alpha_Bessel(self.__cylinder_radius, vibration_frequency, viscosity_limits[1],
                                                    self.__coordinate_series)
                    alpha_max_derivative = Tools.derivative(alpha_max, self.__coordinate_series)[coordinate_index]
                    alpha_middle = self.__Alpha_Bessel(self.__cylinder_radius, vibration_frequency,
                                                       middle_viscosity, self.__coordinate_series)
                    alpha_middle_derivative = Tools.derivative(alpha_middle, self.__coordinate_series)[coordinate_index]
                    simulate_value = np.array([alpha_min_derivative, alpha_middle_derivative, alpha_max_derivative])
                    idx = np.searchsorted(simulate_value, phase_delay_derivative[coordinate_index])
                    if idx == 1:
                        temp = [viscosity_limits[0], middle_viscosity]
                    elif idx == 2:
                        temp = [middle_viscosity, viscosity_limits[1]]
                    else:
                        print("#coordinate_index = " + str(coordinate_index))
                        print("\033[1m\033[31mCALCULATION ERROR：\033[0m" +
                              "The viscosity value at this location may exceed the defined maximum, viscosity may be "
                              "bigger than " + str(max_viscosity) + '.')
                        print(f"\033[1m{'slice':<{slice_width}}{'index':<{coordinate_width}}"
                              f"{'Viscosity':<{viscosity_width}}{'shear_rate':<{shear_rate_width}}\033[0m")
                        viscosity.append(-1)
                        viscosity_limits = [0.5, max_viscosity]
                        err_time += 1
                        break
                    if np.abs(temp[0] - temp[1]) < viscosity_range_tolerance:
                        print(f'{str(window):<{slice_width}}{str(coordinate_index):<{coordinate_width}}'
                              f'{middle_viscosity:<{viscosity_width}.7g}'
                              f'{shear_rate[coordinate_index]:<{shear_rate_width}.5g}')
                        viscosity.append(middle_viscosity)
                        viscosity_limits = [middle_viscosity - visc_range if middle_viscosity - visc_range > 0 else 0.5,
                                            middle_viscosity + visc_range]
                        break
                    else:
                        viscosity_limits = temp
                        middle_viscosity = (viscosity_limits[1] + viscosity_limits[0]) / 2
                if err_time > err_lim and not self.__ignoreUSRException and not ignoreException:
                    break
            if err_time > err_lim:
                if not self.__ignoreUSRException and not ignoreException:
                    print("\033[1m\033[31mCALCULATION BREAK!!!\033[0m")
                    raise USRException("Viscosity at above 1/3 numbers of points may exceed the defined maximum!")
        self.__shear_rate = np.array(shear_rate)
        self.__viscosity = np.array(viscosity)
        print('\033[1m------------------------------------------------------')
        print("Calculation Complete.\033[0m")
        return self.__viscosity, self.__shear_rate,

    def velTableTheta(self, window_num=OFF):
        return self.__vel_data[window_num]

    def timeSeries(self, window_num=OFF):
        return self.__time_series[window_num]

    @property
    def coordSeries(self):
        return self.__coordinate_series

    @property
    def geometry(self):
        return self.__cylinder_radius, self.__delta_y

    @property
    def shearRate(self):
        return self.__shear_rate

    @property
    def viscosity(self):
        return self.__viscosity
