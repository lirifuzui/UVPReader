import threading
from multiprocessing import cpu_count

from scipy.special import jv

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


import pyuvp.uvp
import numpy as np


class Analysis:
    def __init__(self, datas: pyuvp.uvp.readUvpFile = None, tdx_num: int = OFF,
                 vel_data: list[np.ndarray] | None = None,
                 time_series: list[np.ndarray] | None = None, coordinate_series: list[np.ndarray] | None = None,
                 ignoreException=False,
                 num_threads: int = 1):
        """
        analysis class for creating rheological analyzes from Uvp datas.

        Parameters:
            - datas: pyuvp.uvp.readUvpFile object containing the data for analysis. Default is None.
            - tdx_num: int, data index. Default is OFF.
            - vel_data: list[np.ndarray] | None, list of velocity data. Default is None.
            - time_series: list[np.ndarray] | None, list of time series. Default is None.
            - coordinate_series: list[np.ndarray] | None, list of coordinate series. Default is None.
            - ignoreException: bool, whether to ignore exceptions. Default is False.
        """

        # Considering that the velocity data will be time-sliced later,
        # self.__vel_data and self.__time_array are stored in a list,
        # where each item corresponds to a window.
        # The lengths of self.__vel_data and self.__time_array should be equal.
        # self.__vel_data stores the pruned analyzable data and is initialized to store the complete data.
        self.__vel_data: list[np.ndarray] = [datas.velTables[tdx_num] if datas else vel_data[tdx_num]]
        self.__time_array: list[np.ndarray] = [datas.timeArrays[tdx_num] if datas else time_series[tdx_num]]
        self.__coordinate_array: np.ndarray = datas.coordinateArrays[tdx_num] if datas else coordinate_series[tdx_num]

        self.__temp_vel: list[np.ndarray] = [datas.velTables[tdx_num] if datas else vel_data[tdx_num]]
        self.__temp_coords: np.ndarray = datas.coordinateArrays[tdx_num] if datas else coordinate_series[tdx_num]

        # Store the pruned analyzable data and initialize it to store the complete data.
        # Number of windows, default is 1.
        self.__number_of_windows: int = 0
        self.__slice: list[list[int]] = [[0, len(self.__time_array[0]) - 1]]

        self.__cylinder_radius: float | None = None
        self.__delta_y = None

        self.__pipe_TDXangle: float | None = None

        self.__shear_freq = None

        self.__shear_rate: np.ndarray | None = None
        self.__viscosity_cSt: np.ndarray | None = None

        self.__viscosity_Pas: np.ndarray | None = None
        self.__viscoelastic_delta: np.ndarray | None = None

        self.__err_time: int = 0

        self.__ignoreUSRException = ignoreException

        # Number of calling threads
        def check_value(input_value, threshold):
            if input_value > threshold:
                raise ValueError("The number of calling threads exceeds")

        try:
            check_value(num_threads, cpu_count())
            self.__num_threads = num_threads
        except ValueError as e:
            print(e)

    # Update the variable self.__coordinate_array and self.__vel_data,
    # to store the data in the radial coordinate system.
    # If you don't execute these two functions, the variable will store the coordinates in the xi coordinate system.
    # Running this function will modify the data in self.__coordinate_array and self.__vel_data,
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
            self.__shear_freq = vibration_params[0]
            max_vel = 2 * np.pi * self.__shear_freq * self.__cylinder_radius * (vibration_params[1] * np.pi / 180)
            self.__vel_data, self.__temp_vel = self.__temp_vel, self.__vel_data
            self.__coordinate_array, self.__temp_coords = self.__temp_coords, self.__coordinate_array
            _, max_magnitude, _, _, _, _ = self.fftInUSR()
            wall_coordinate = self.__coordinate_array[np.argmax(max_magnitude)]
            self.__coordinate_array, self.__temp_coords = self.__temp_coords, self.__coordinate_array
            self.__vel_data, self.__temp_vel = self.__temp_vel, self.__vel_data
            self.__delta_y = self.__cylinder_radius * np.max(max_magnitude) / max_vel
            if self.__delta_y > self.__cylinder_radius:
                raise ValueError("Delta y is greater than the cylinder radius!")
        # Update the variable self.__coordinate_array
        half_chord = np.sqrt(radius ** 2 - self.__delta_y ** 2)
        self.__coordinate_array = np.sqrt((wall_coordinate + half_chord -
                                           self.__coordinate_array) ** 2 + self.__delta_y ** 2)
        # Update the variable self.__vel_data
        for i in range(self.__number_of_windows + 1):
            self.__vel_data[i] = self.__vel_data[i] * self.__coordinate_array / self.__delta_y
        return self.__vel_data, self.__coordinate_array

    def pipeGeom(self, pipe_TDXangle, flow_freq):
        # 这里的角度是与半径方向的夹角
        self.__pipe_TDXangle = pipe_TDXangle
        self.__shear_freq = flow_freq
        self.__coordinate_array = self.__coordinate_array * np.cos(self.__pipe_TDXangle / 180 * np.pi)
        for i in range(self.__number_of_windows + 1):
            self.__vel_data[i] = self.__vel_data[i] * np.sin(self.__pipe_TDXangle / 180 * np.pi)

    # Extracted vaild data according to the position coordinates.
    def channelRange(self, start: int = 0, end: int = -1):
        for i in range(self.__number_of_windows + 1):
            self.__vel_data[i] = self.__vel_data[i][:, start:end]
        self.__coordinate_array = self.__coordinate_array[start:end]

    def slicing(self, number_of_slice: int = 5, slice_size: None | int = None, ignoreException=False):
        self.__number_of_windows = number_of_slice
        max_index = self.__slice[0][1]

        if number_of_slice == 1 or number_of_slice == 0:
            self.__number_of_windows = 0
            self.__time_array = self.__time_array[:1]
            self.__vel_data = self.__vel_data[:1]
            self.__slice = self.__slice[:1]

        elif number_of_slice == 2:
            self.__time_array = [self.__time_array[0],
                                 self.__time_array[0][0: max_index // 2],
                                 self.__time_array[0][max_index // 2: max_index]]
            self.__vel_data = [self.__vel_data[0],
                               self.__vel_data[0][0: max_index // 2, :],
                               self.__vel_data[0][max_index // 2: max_index:, :]]
            self.__slice = [self.__slice[0],
                            [0, max_index // 2],
                            [max_index // 2, max_index]]

        else:  # number_of_size >= 3
            self.__time_array = [self.__time_array[0]]
            self.__vel_data = [self.__vel_data[0]]
            self.__slice = [self.__slice[0]]
            moving = max_index // ((number_of_slice - 1) * 2)
            for slice_index in range(number_of_slice):
                start = 0 + slice_index * moving
                end = max_index - (number_of_slice - 1 - slice_index) * moving
                self.__time_array.append(self.__time_array[0][start:end])
                self.__vel_data.append(self.__vel_data[0][start:end, :])
                self.__slice.append([start, end])
        if slice_size is not None:
            self.sliceSize(slice_size, ignoreException)

    def sliceSize(self, slice_length, ignoreException=False):
        if slice_length < self.__slice[0][1] // self.__number_of_windows and not ignoreException:
            raise USRException("The slice length is not enough to cover all the data!")
        if self.__number_of_windows == 1 or self.__number_of_windows == 2:
            raise USRException("Too few slices to change length!")

        temp_slice = self.__slice[:1]
        temp_slice.append([0, slice_length - 1])
        moving = (self.__slice[0][1] + 1 - slice_length) // (self.__number_of_windows - 1)
        for n in range(self.__number_of_windows - 2):
            temp_slice.append([0 + moving * (n + 1), slice_length + moving * (n + 1)])
        temp_slice.append([self.__slice[0][1] - slice_length, self.__slice[0][1]])
        self.__slice = temp_slice
        self.__time_array = [self.__time_array[0][slice_range[0]:slice_range[1]] for slice_range in self.__slice]
        self.__vel_data = [self.__vel_data[0][slice_range[0]:slice_range[1]] for slice_range in self.__slice]

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
        beta = np.sqrt(-1j * 2 * np.pi * freq_0 / visc)
        bR = beta * cylinder_R
        J_R = jv(1, bR)
        Phi_R, Psi_R = np.real(J_R), np.imag(J_R)
        br = beta * coordinates_r
        J_r = jv(1, br)
        Phi_r, Psi_r = np.real(J_r), np.imag(J_r)
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

    def sinWaveFilter(self, window_num: int = 1, derivative_smoother_factor: int = 11):
        None

    # do the FFT.
    def fftInUSR(self, window_num: int = 1, derivative_smoother_factor: int = 11):
        my_axis = 0
        N = len(self.__time_array[window_num - 1])
        Delta_T = (self.__time_array[window_num - 1][-1] - self.__time_array[window_num - 1][0]) / (N - 1)
        fft_result = np.fft.rfft(self.__vel_data[window_num - 1], axis=my_axis)
        magnitude = np.abs(fft_result)
        max_magnitude_indices = np.argmax(magnitude, axis=my_axis)
        freq_array = np.fft.rfftfreq(N, Delta_T)
        oscillation_frequency = np.mean(np.abs(freq_array[max_magnitude_indices]))
        max_magnitude = np.abs(fft_result[max_magnitude_indices, range(fft_result.shape[1])]) / N
        phase_delay = np.angle(fft_result[max_magnitude_indices, range(fft_result.shape[1])])
        phase_delay = self.__phase_unwrap(phase_delay)
        phase_delay -= phase_delay[np.argmax(self.__coordinate_array)]
        phase_delay = np.abs(phase_delay)

        phase_delay_derivative = Tools.derivative(phase_delay, self.__coordinate_array, derivative_smoother_factor)

        real_part = fft_result[max_magnitude_indices, range(fft_result.shape[1])].real / N
        imag_part = fft_result[max_magnitude_indices, range(fft_result.shape[1])].imag / N
        return oscillation_frequency, max_magnitude, phase_delay, phase_delay_derivative, real_part, imag_part

    # Calculate Viscosity and Shear Rate.
    def rheologyViscosity(self, max_viscosity: int | float = 20000,
                          viscosity_range_tolerance: int | float = 1,
                          smooth_level: int = 11, ignoreException=False):
        # max_viscosity _cSt
        # viscosity_range_tolerance _cSt
        if len(self.__coordinate_array) < 20 and ignoreException == False:
            raise USRException("The number of coordinate must be greater than 20!")
        if self.__cylinder_radius is None and self.__pipe_TDXangle is None:
            raise ValueError("You must define Container Geometry first！")
        effective_shear_rate = []
        effective_viscosity = []
        err_lim = len(self.__coordinate_array) // \
                  (1 / ExceptionConfig['Allowable proportion of calculation error points'])
        # Format the output.
        slice_width = 8
        index_width = 8
        search_range_width = 26
        viscosity_width = 16
        shear_rate_width = 10
        print("\033[1mCalculation Start:")
        print('------------------------------------------------------')
        for window in range(self.__number_of_windows + 1):
            oscillation_frequency, _, _, phase_delay_derivative, real_part, imag_part = \
                self.fftInUSR(window_num=window, derivative_smoother_factor=smooth_level)
            self.__shear_freq = oscillation_frequency if self.__shear_freq is None else self.__shear_freq

            # Determine whether the frequency of the input container matches the experimental results.
            if np.abs(oscillation_frequency - self.__shear_freq) > \
                    np.abs(
                        oscillation_frequency * ExceptionConfig['Allowable magnification of frequency difference']) \
                    and not self.__ignoreUSRException and not ignoreException:
                raise USRException(
                    "The defined vibration frequency of the cylinder does not match the results of the "
                    "experimental data! [" + f"{oscillation_frequency:.3g}" + ", " + str(
                        self.__shear_freq) + "]")

            # print title
            print(f"{'slice':<{8}}{'time_range':<{16}}{'vessel_freq':<{8}}")
            print(f"{window:<{8}}{str(self.__slice[window]):<{16}}{oscillation_frequency:<{8}.7g}")
            print(f"{'slice':<{slice_width}}{'index':<{index_width}}{'search_range(cycles)':<{search_range_width}}"
                  f"{'Viscosity':<{viscosity_width}}{'effective_shear_rate':<{shear_rate_width}}\033[0m")

            # Calculate effective shear rate.
            real_part_derivative = Tools.derivative(real_part, self.__coordinate_array,
                                                    derivative_smoother_factor=5)
            imag_part_derivative = Tools.derivative(imag_part, self.__coordinate_array,
                                                    derivative_smoother_factor=5)
            param_1 = real_part_derivative - (real_part / self.__coordinate_array)
            param_2 = imag_part_derivative - (imag_part / self.__coordinate_array)
            shear_rate_for_now_window = np.sqrt(param_1 ** 2 + param_2 ** 2)
            effective_shear_rate.extend(shear_rate_for_now_window)

            effective_viscosity_for_now_window = [0] * len(self.__coordinate_array)

            def multithread_Calculate_viscosity(Start, End):
                # Calculate viscosity.
                viscosity_limits = [0.5, max_viscosity]
                visc_range = int((max_viscosity - 0.5) / 40)

                for n, coordinate_index in enumerate(range(Start, End)):
                    loop_count = int(np.log2(viscosity_limits[1] - viscosity_limits[0])) + 10
                    middle_viscosity = (viscosity_limits[1] + viscosity_limits[0]) / 2
                    first_search_range_of_loop = viscosity_limits.copy()
                    for loop in range(loop_count):
                        alpha_min = self.__Alpha_Bessel(self.__cylinder_radius, oscillation_frequency,
                                                        viscosity_limits[0],
                                                        self.__coordinate_array)
                        alpha_min -= alpha_min[np.argmax(self.__coordinate_array)]
                        alpha_min = np.abs(alpha_min)
                        alpha_min_derivative = Tools.derivative(alpha_min, self.__coordinate_array)[coordinate_index]
                        alpha_max = self.__Alpha_Bessel(self.__cylinder_radius, oscillation_frequency,
                                                        viscosity_limits[1],
                                                        self.__coordinate_array)
                        alpha_max -= alpha_max[np.argmax(self.__coordinate_array)]
                        alpha_max = np.abs(alpha_max)
                        alpha_max_derivative = Tools.derivative(alpha_max, self.__coordinate_array)[coordinate_index]
                        alpha_middle = self.__Alpha_Bessel(self.__cylinder_radius, oscillation_frequency,
                                                           middle_viscosity, self.__coordinate_array)
                        alpha_middle -= alpha_middle[np.argmax(self.__coordinate_array)]
                        alpha_middle = np.abs(alpha_middle)
                        alpha_middle_derivative = Tools.derivative(alpha_middle, self.__coordinate_array)[
                            coordinate_index]
                        simulate_value = np.array([alpha_min_derivative, alpha_middle_derivative, alpha_max_derivative])
                        idx = np.searchsorted(simulate_value, phase_delay_derivative[coordinate_index])
                        if idx == 1:
                            temp = [viscosity_limits[0], middle_viscosity]
                        elif idx == 2:
                            temp = [middle_viscosity, viscosity_limits[1]]
                        else:
                            print(f'{window:<{slice_width}}{coordinate_index:<{index_width}}'
                                  f'[{first_search_range_of_loop[0]:<{8}.5g},{first_search_range_of_loop[1]:<{8}.5g}]({loop:<{2}})'
                                  f'   '
                                  f'{"ERROR":<{viscosity_width}}'
                                  f'{shear_rate_for_now_window[coordinate_index]:<{shear_rate_width}.5g}')
                            print("\033[1m\033[31mCALCULATION ERROR：\033[0m" +
                                  "The effective_viscosity value at this location may exceed the defined maximum"
                                  "(" + str(max_viscosity) + ').')
                            effective_viscosity_for_now_window[Start + n] = -1
                            viscosity_limits = [0.5, max_viscosity]
                            self.__err_time += 1
                            break
                        if np.abs(temp[0] - temp[1]) < viscosity_range_tolerance:
                            print(f'{window:<{slice_width}}{coordinate_index:<{index_width}}'
                                  f'[{first_search_range_of_loop[0]:<{8}.5g},{first_search_range_of_loop[1]:<{8}.5g}]({loop:<{2}})'
                                  f'   '
                                  f'{middle_viscosity:<{viscosity_width}.7g}'
                                  f'{shear_rate_for_now_window[coordinate_index]:<{shear_rate_width}.5g}')
                            effective_viscosity_for_now_window[Start + n] = middle_viscosity
                            viscosity_limits = [
                                middle_viscosity - visc_range if middle_viscosity - visc_range > 0 else 0.5,
                                middle_viscosity + visc_range]
                            break
                        else:
                            viscosity_limits = temp
                            middle_viscosity = (viscosity_limits[1] + viscosity_limits[0]) / 2
                    if self.__err_time > err_lim and not self.__ignoreUSRException and not ignoreException:
                        break
                if self.__err_time > err_lim:
                    if not self.__ignoreUSRException and not ignoreException:
                        print("\033[1m\033[31mCALCULATION BREAK!!!\033[0m")
                        raise USRException("Viscosity at above 1/3 numbers of points may exceed the defined maximum!")

            threads = []
            if len(self.__coordinate_array) // self.__num_threads >= 1:
                point_per_thread = len(self.__coordinate_array) // self.__num_threads
                for thread_number in range(self.__num_threads):
                    start = thread_number * point_per_thread
                    end = start + point_per_thread if thread_number < self.__num_threads - 1 else len(
                        self.__coordinate_array)
                    thread = threading.Thread(target=multithread_Calculate_viscosity, args=(start, end))
                    threads.append(thread)
            else:
                point_per_thread = 1
                for thread_number in range(len(self.__coordinate_array)):
                    start = thread_number * point_per_thread
                    end = start + 1
                    thread = threading.Thread(target=multithread_Calculate_viscosity, args=(start, end))
                    threads.append(thread)

            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            effective_viscosity.extend(effective_viscosity_for_now_window)

        self.__shear_rate = np.array(effective_shear_rate)
        self.__viscosity_cSt = np.array(effective_viscosity)

        print('\033[1m------------------------------------------------------')
        print("Calculation Complete.\033[0m")
        return self.__viscosity_cSt, self.__shear_rate

    def rheologyViscoelasticity(self, density, max_viscosity: int | float = 30000,
                                smooth_level: int = 11, ignoreException=False):
        # density _kg/m3
        # max_viscosity _cSt
        if len(self.__coordinate_array) < 20:
            raise USRException("The number of channels is less than 20!")
        if self.__cylinder_radius is None:
            raise ValueError("You must define cylinder container Geometry first！")
        useful_range = [4, -4]
        shear_rate = []
        cost_function = []
        delta = []
        viscosity = []
        deltas = np.linspace(0.01, np.pi / 2 - 0.01, 100)
        viscositys = np.linspace(0.001, max_viscosity * density / (10 ** 6), max_viscosity)

        # Format the output.
        slice_width = 8
        index_width = 8
        viscoelasticity_width = 16
        viscosity_width = 16
        shear_rate_width = 10
        print("\033[1mCalculation Start:")
        print('------------------------------------------------------')

        coordinate_series = self.__coordinate_array * 0.001
        for window in range(self.__number_of_windows + 1):
            oscillation_frequency, _, _, _, real_part, imag_part = self.fftInUSR(window_num=window,
                                                                                 derivative_smoother_factor=smooth_level)
            # Calculate effective shear rate.
            real_part_derivative = Tools.derivative(real_part * 0.001, coordinate_series,
                                                    derivative_smoother_factor=5)
            imag_part_derivative = Tools.derivative(imag_part * 0.001, coordinate_series,
                                                    derivative_smoother_factor=5)
            param_1 = real_part_derivative - (real_part * 0.001 / coordinate_series)
            param_2 = imag_part_derivative - (imag_part * 0.001 / coordinate_series)
            shear_rate_of_now_window = np.sqrt(param_1 ** 2 + param_2 ** 2)
            shear_rate.extend(shear_rate_of_now_window[useful_range[0]: useful_range[1]])
            # Calculate viscoelastcity.
            Re = param_1 + (param_2 / np.tan(deltas.reshape((-1, 1))))
            Im = -(param_1 / np.tan(deltas.reshape((-1, 1)))) + param_2
            Re_derivative = np.gradient(Re, coordinate_series, axis=1)
            Im_derivative = np.gradient(Im, coordinate_series, axis=1)

            cost_function_of_now_window = []
            delta_of_now_window = []
            viscosity_of_now_window = []
            for coordinate_index in range(len(coordinate_series)):
                Re_r = Re[:, coordinate_index]
                Im_r = Im[:, coordinate_index]
                Re_derivative_r = Re_derivative[:, coordinate_index]
                Im_derivative_r = Im_derivative[:, coordinate_index]
                coordinate = coordinate_series[coordinate_index]
                param_2_1 = (Re_derivative_r + (Re_r * 2 / coordinate)).reshape((-1, 1)) * (
                        np.sin(deltas.reshape((-1, 1))) ** 2)
                param_2_2 = (Im_derivative_r + (Im_r * 2 / coordinate)).reshape((-1, 1)) * (
                        np.sin(deltas.reshape((-1, 1))) ** 2)
                cost_funciton_r = ((2 * np.pi * oscillation_frequency * density * imag_part[coordinate_index] * 0.001)
                                   + (viscositys * param_2_1)) ** 2 + \
                                  ((2 * np.pi * oscillation_frequency * density * real_part[coordinate_index] * 0.001)
                                   - (viscositys * param_2_2)) ** 2
                min_index_flat = np.argmin(cost_funciton_r)
                min_index = np.unravel_index(min_index_flat, cost_funciton_r.shape)

                cost_function_of_now_window.append(cost_funciton_r)
                delta_of_now_window.append(deltas[min_index[0]])
                viscosity_of_now_window.append(viscositys[min_index[1]])

            cost_function.extend(cost_function_of_now_window[useful_range[0]: useful_range[1]])
            delta.extend(delta_of_now_window[useful_range[0]: useful_range[1]])
            viscosity.extend(viscosity_of_now_window[useful_range[0]: useful_range[1]])
            print("ok")

        self.__shear_rate = np.array(shear_rate)
        self.__viscosity_Pas = np.array(viscosity)
        self.__viscoelastic_delta = np.array(delta)
        return self.__shear_rate, self.__viscosity_Pas, self.__viscoelastic_delta, cost_function

    def velTableTheta(self, window_num=OFF):
        return self.__vel_data[window_num]

    def timeSeries(self, window_num=OFF):
        return self.__time_array[window_num]

    @property
    def coordSeries(self):
        return self.__coordinate_array

    @property
    def geometry(self):
        return self.__cylinder_radius, self.__delta_y
