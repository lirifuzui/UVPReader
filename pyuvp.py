from struct import unpack
import numpy as np

import Tools

ON = 1
OFF = 0


class ReadData:
    def __init__(self, file_path):
        # To store the important UVP configuration parameters
        self.__measurement_info = {}
        self.__mux_config_params = {}

        # Velocity file_data, echo_data file_data and time series are each stored in a list.
        # Each item in the list corresponds to data from a tdx.
        # Notice! ! !
        # When using mux, due to the physical conversion of the signal output of tdx,
        # The time delay set by the user should meet at least 200 ms.
        self.__vel_data_list = []
        self.__echo_data_list = []
        self.__time_series_list = []
        # Although the coordinate series of each tdx data is the same, it is still stored in a list for ease of use.
        # Each item of the list is the same coordinate series.
        self.__coordinate_series_list = []

        # Run the function “__read_data”, and store the data in the corresponding class variables respectively.
        self.__read_data(file_path)

        # 实例化统计和分析数据类。
        # self.statistic = Statistic(vel_data=self.velTable, echo_data=self.echoTable)

    def __read_params_part_I(self, uvp_datafile) -> None:
        # Read parameter information at the beginning of the file.
        # The file_data structure is as follows:
        """signum, line char [64]
        measParamsOffset1, line unsigned long
        measParamsOffset2", line unsigned long
        nProfiles, line unsigned long
        reserved1, line unsigned long
        flags, line unsigned long
        recordsize, line unsigned long
        nChannels, line unsigned long
        reserved2, line unsigned long
        startTime1, line unsigned long
        startTime2, line unsigned long """

        uvp_datafile.seek(64)
        head_params = [unpack('L', uvp_datafile.read(4)) for _ in range(10)]
        self.__measurement_info['NumberOfChannels'] = int(head_params[6][0])
        self.__measurement_info['NumberOfProfiles'] = int(head_params[2][0])

    # noinspection PyTypeChecker
    def __read_params_part_II(self, uvp_datafile) -> None:
        # Read parameter information at the bottom of the file.
        # Including 'UVP PARAMETER' and 'MUX PARAMETER' two parts.
        uvp_datafile.seek(0)
        foot_datas = uvp_datafile.read()
        uvp_params_begin = foot_datas.find(b"[UVP_PARAMETER]")
        uvp_datafile.seek(uvp_params_begin)
        lines = uvp_datafile.readlines()
        # Divide the file_data list into two lists, 'uvp_operational_params_list' and 'mux_config_params_list'.
        index = lines.index(b'[MUX_PARAMETER]\n')
        uvp_operational_params_list = [item.decode('utf-8', errors='replace') for item in lines[1:index]]
        mux_config_params_list = [item.decode('utf-8', errors='replace') for item in lines[index + 1:]]
        uvp_operational_params_list = [item.strip() for item in uvp_operational_params_list]
        mux_config_params_list = [item.strip() for item in mux_config_params_list]
        mux_config_params_list = [item.replace('\\', '') for item in mux_config_params_list]

        index_1 = [i for i, line in enumerate(uvp_operational_params_list) if line.startswith('Comment=')][0]
        index_2 = [i for i, line in enumerate(uvp_operational_params_list) if
                   line.startswith('MeasurementProtocol=')][0]
        index_3 = [i for i, line in enumerate(mux_config_params_list) if line.startswith('Table=')][0]
        for item in uvp_operational_params_list[:index_1]:
            if not item:
                continue
            parts = item.split("=")
            name = parts[0].strip()
            value = None if parts[1].strip() == '' else parts[1].strip()
            if value.replace('.', '').replace('-', '').isdigit():
                value = float(value)
            self.__measurement_info[name] = value
        comment_value = "\n".join(uvp_operational_params_list[index_1:index_2]).replace("Comment=", "")
        self.__measurement_info["Comment"] = None if comment_value == '' else comment_value
        protocol_value = "\n".join(uvp_operational_params_list[index_2:]).replace("MeasurementProtocol=", "")
        self.__measurement_info["MeasurementProtocol"] = None if protocol_value == '' else protocol_value

        for item in mux_config_params_list[:index_3 + 1]:
            if not item:
                continue
            parts = item.split("=")
            name = parts[0].strip()
            value = None if parts[1].strip() == '' else parts[1].strip()
            if value.replace('.', '').replace('-', '').isdigit():
                value = float(value)
            self.__mux_config_params[name] = value
        mux_config = [list(map(float, item.split())) for item in mux_config_params_list[index_3 + 1:]]
        self.__mux_config_params['MultiplexerConfiguration'] = mux_config

    def resetSoundSpeed(self, sound_speed) -> None:
        self.__measurement_info['SoundSpeed'] = sound_speed
        max_depth = self.__measurement_info['MaximumDepth']
        doppler_coefficient = sound_speed / (max_depth * 2.0) / 256.0 * 1000.0
        sounds_speed_coefficient = sound_speed / (self.__measurement_info['Frequency'] * 2.0)

        if self.__measurement_info['UseMultiplexer']:
            self.__vel_data_list = [[] for _ in range(int(self.__mux_config_params['Table']))]
            self.__echo_data_list = [[] for _ in range(int(self.__mux_config_params['Table']))]
            self.__time_series_list = [[] for _ in range(int(self.__mux_config_params['Table']))]

            time_series = np.arange(0, self.__measurement_info['NumberOfProfiles'] *
                                    self.__measurement_info['SampleTime'], self.__measurement_info['SampleTime'])
            time_plus = 0
            temp_vel_data = self.__raw_vel_data
            temp_echo_data = self.__raw_echo_data
            while list(temp_vel_data):
                now_index = 0
                for tdx in range(int(self.__mux_config_params['Table'])):
                    if self.__mux_config_params['MultiplexerConfiguration'][tdx][0]:
                        number_of_read_lines = int(self.__mux_config_params['MultiplexerConfiguration'][tdx][2])
                        self.__vel_data_list[tdx].extend(
                            temp_vel_data[now_index:now_index + number_of_read_lines])
                        self.__echo_data_list[tdx].extend(
                            temp_echo_data[now_index:now_index + number_of_read_lines])
                        now_index += number_of_read_lines
                        self.__time_series_list[tdx].extend(
                            time_series[now_index:now_index + number_of_read_lines] + time_plus)
                        if tdx + 1 < int(self.__mux_config_params['Table']):
                            time_plus += self.__mux_config_params['MultiplexerConfiguration'][tdx + 1][3]
                        else:
                            time_plus += self.__mux_config_params['MultiplexerConfiguration'][0][3]
                    else:
                        continue
                temp_vel_data = temp_vel_data[now_index:]
                temp_echo_data = temp_echo_data[now_index:]
                time_series = time_series[now_index:]
                time_plus += self.__mux_config_params['CycleDelay']
            self.__vel_data_list = [np.array(item) for item in self.__vel_data_list]
            self.__echo_data_list = [np.array(item) for item in self.__echo_data_list]

        else:
            angle_coefficient = 1.0 / np.sin(self.__measurement_info['Angle'] * np.pi / 180)
            vel_resolution = doppler_coefficient * sounds_speed_coefficient * 1000 * angle_coefficient
            vel_data = self.__raw_vel_data * vel_resolution
            echo_data = self.__raw_echo_data
            self.__vel_data_list.append(vel_data)
            self.__echo_data_list.append(echo_data)

            time_series = np.arange(0, self.__measurement_info['NumberOfProfiles'] *
                                    self.__measurement_info['SampleTime'], self.__measurement_info['SampleTime'])
            self.__time_series_list.append(time_series * 0.001)

        # Store multiple coordinate series of tdx data into a list
        coordinate_series = np.arange(self.__measurement_info['StartChannel'], self.__measurement_info['StartChannel'] +
                                      self.__measurement_info['NumberOfChannels'] * self.__measurement_info[
                                          'ChannelDistance'],
                                      self.__measurement_info['ChannelDistance'])
        if int(self.__mux_config_params['Table']):
            self.__coordinate_series_list = [coordinate_series for _ in range(int(self.__mux_config_params['Table']))]
        else:
            self.__coordinate_series_list.append(coordinate_series)

    def __read_data(self, file_path) -> None:
        with open(file_path, 'rb') as uvpDatafile:
            self.__read_params_part_I(uvpDatafile)
            self.__read_params_part_II(uvpDatafile)

            # read velocity file_data and echo_data file_data
            self.__raw_vel_data = np.zeros((self.__measurement_info['NumberOfProfiles'],
                                            self.__measurement_info['NumberOfChannels']))
            self.__raw_echo_data = np.zeros((self.__measurement_info['NumberOfProfiles'],
                                             self.__measurement_info['NumberOfChannels']))
            uvpDatafile.seek(104)
            for i in range(self.__measurement_info['NumberOfProfiles']):
                uvpDatafile.seek(16, 1)
                if self.__measurement_info['DoNotStoreDoppler']:
                    None
                else:
                    encode_vel_data = uvpDatafile.read(self.__measurement_info['NumberOfChannels'] * 2)
                    datatype = '{}h'.format(self.__measurement_info['NumberOfChannels'])
                    self.__raw_vel_data[i] = unpack(datatype, encode_vel_data)
                if self.__measurement_info['AmplitudeStored']:
                    encode_echo_data = uvpDatafile.read(self.__measurement_info['NumberOfChannels'] * 2)
                    self.__raw_echo_data[i] = unpack(datatype, encode_echo_data)
        # Resolution the velocity file_data, echo_data file_data, time series and coordinate series.
        self.resetSoundSpeed(self.__measurement_info['SoundSpeed'])

    def createAnalysis(self, tdx_num=0):
        return Analysis(vel_data=self.velTables, tdx_num=tdx_num, time_series=self.timeSeries,
                        coordinate_series=self.coordinateSeries)

    @property
    def muxStatus(self):
        return 'On' if self.__measurement_info['UseMultiplexer'] else 'OFF'

    def velTables(self, tdx_num=0):
        return self.__vel_data_list[tdx_num]

    def echoTables(self, tdx_num=0):
        return self.__echo_data_list[tdx_num]

    def timeSeries(self, tdx_num=0):
        return self.__time_series_list[tdx_num]

    def coordinateSeries(self, tdx_num=0):
        return self.__coordinate_series_list[tdx_num]

    def show_info(self):
        None

    def get_log(self):
        None


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
        # Update the variable self.__vel_data
        trans_arr = delta_y * np.reciprocal(self.__coordinate_series)
        for i in range(self.__number_of_windows):
            self.__analyzable_vel_data[i] = np.multiply(self.__analyzable_vel_data[i], trans_arr)
        return self.__analyzable_vel_data, self.__coordinate_series

    def settingInterCylinder(self, cylinder_r, wall_coordinates_xi, delta_y):
        None

    def extract_analyzable_data(self, extract_range=[0, -1]):
        for i in range(self.__number_of_windows):
            self.__analyzable_vel_data[i] = self.__analyzable_vel_data[i][:, extract_range[0]:extract_range[1]]
        self.__coordinate_series = self.__coordinate_series[extract_range[0]:extract_range[1]]

    # do the FFT.
    def do_fft(self, window_num=0, derivative_smoother_factor=[7, 1]):
        my_axis = 0
        fft_result = np.fft.rfft(self.__analyzable_vel_data[window_num], axis=my_axis)
        magnitude = np.abs(fft_result)
        max_magnitude_indices = np.argmax(magnitude, axis=my_axis)
        max_magnitude = np.abs(fft_result[max_magnitude_indices, range(fft_result.shape[1])]) / len(
            self.__time_series[window_num])
        phase_delay = np.angle(fft_result[max_magnitude_indices, range(fft_result.shape[1])])
        for i in range(1, len(phase_delay)):
            dphase = phase_delay[i] - phase_delay[i - 1]
            condition1 = dphase > np.pi
            condition2 = dphase < -np.pi
            phase_delay[i:] -= np.where(condition1, 2 * np.pi, np.where(condition2, -2 * np.pi, 0))
        phase_delay += phase_delay[0]
        phase_delay = np.abs(phase_delay)

        phase_delay_derivative = Tools.derivative(phase_delay, self.__coordinate_series, derivative_smoother_factor)
        real_part = fft_result[max_magnitude_indices, range(fft_result.shape[1])].real / len(
            self.__time_series[window_num])
        imag_part = fft_result[max_magnitude_indices, range(fft_result.shape[1])].imag / len(
            self.__time_series[window_num])
        return max_magnitude, phase_delay, phase_delay_derivative, real_part, imag_part

    # Calculate effective shear rate, contains the section that do the FFT.
    def calculate_effective_shear_rate(self, window_num=0):
        _, _, _, real_part, imag_part = self.do_fft(window_num=window_num)
        real_part_derivative = Tools.derivative(real_part, self.__coordinate_series)
        imag_part_derivative = Tools.derivative(imag_part, self.__coordinate_series)
        param_1 = real_part_derivative - (real_part / self.__coordinate_series)
        param_2 = imag_part_derivative - (imag_part / self.__coordinate_series)
        self.__shear_rate = np.sqrt(param_1 ** 2 + param_2 ** 2)
        return self.__shear_rate

    def doanaylsis(self):
        None

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
