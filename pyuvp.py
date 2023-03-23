from struct import unpack
import numpy as np

import Tools

ON = 1
OFF = 0


class ReadData:

    def __init__(self, file_path, read_as_mux=OFF):
        self.__measurement_info = {}
        self.__mux_config_params = {}

        # Velocity file_data and echo file_data may be two-dimensional arrays or three-dimensional arrays.
        # 如果没有开多传感器的话存在这里，是一个numpy的二维数组
        self.__vel_data = None
        self.__echo_data = None
        # 如果开了多传感器的话存在这里，是一个一维列表，里面的每一项对应一个传感器的数据，是一个numpy的二维数组。
        self.__mux_vel_data_list = None
        self.__mux_echo_data_list = None
        # 不管有没有开mux，都会坐标序列存储在一个numpy数组中
        self.__coordinate_series = None

        # 运行内部函数，读取数据，将结果分散存储在类变量中。
        self.__read_data(file_path)

        # 实例化统计和分析数据类。
        self.statistic = Statistic(vel_data=self.velTable, echo_data=self.echoTable)
        self.analysis = Analysis(vel_data=self.velTable, sample_time=self.sampleTime, nprofile=self.numberOfProfile,
                                 coordinate_series=self.coordinateSeries)

        print(self.__mux_config_params)

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
            self.__mux_vel_data_list = [[] for _ in range(int(self.__mux_config_params['Table']))]
            self.__mux_echo_data_list = [[] for _ in range(int(self.__mux_config_params['Table']))]
            temp_vel_data = self.__raw_vel_data
            temp_echo_data = self.__raw_echo_data
            while list(temp_vel_data):
                now_index = 0
                for tdx in range(int(self.__mux_config_params['Table'])):
                    if self.__mux_config_params['MultiplexerConfiguration'][tdx][0]:
                        number_of_read_lines = int(self.__mux_config_params['MultiplexerConfiguration'][tdx][2])
                        self.__mux_vel_data_list[tdx].extend(
                            temp_vel_data[now_index:now_index + number_of_read_lines])
                        self.__mux_echo_data_list[tdx].extend(
                            temp_echo_data[now_index:now_index + number_of_read_lines])
                        now_index += number_of_read_lines
                    else:
                        continue
                temp_vel_data = temp_vel_data[now_index:]
                temp_echo_data = temp_echo_data[now_index:]
            self.__mux_vel_data_list = [np.array(item) for item in self.__mux_vel_data_list]
            self.__mux_echo_data_list = [np.array(item) for item in self.__mux_echo_data_list]

        else:
            angle_coefficient = 1.0 / np.sin(self.__measurement_info['Angle'] * np.pi / 180)
            vel_resolution = doppler_coefficient * sounds_speed_coefficient * 1000 * angle_coefficient
            self.__vel_data = self.__raw_vel_data * vel_resolution
            self.__echo_data = self.__raw_echo_data

        self.__coordinate_series = [
            self.__measurement_info['StartChannel'] + n * self.__measurement_info['ChannelDistance']
            for n in range(self.__measurement_info['NumberOfChannels'])]

    def __read_data(self, file_path) -> None:
        with open(file_path, 'rb') as uvpDatafile:
            self.__read_params_part_I(uvpDatafile)
            self.__read_params_part_II(uvpDatafile)

            # read velocity file_data and echo file_data
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
        # Resolution the velocity file_data, echo file_data, time series and coordinate series.
        self.resetSoundSpeed(self.__measurement_info['SoundSpeed'])

    @property
    def muxState(self):
        return self.__measurement_info['UseMultiplexer']

    @property
    def velTable(self):
        return self.__mux_vel_data_list if self.muxState else self.__vel_data

    @property
    def echoTable(self):
        return self.__mux_echo_data_list if self.muxState else self.__echo_data

    @property
    def sampleTime(self):
        return self.__measurement_info['SampleTime']

    @property
    def numberOfProfile(self):
        return self.__measurement_info['NumberOfProfiles']

    @property
    def coordinateSeries(self):
        return self.__coordinate_series

    @property
    def summaryData(self):
        return self.velTable, self.echoTable, self.sampleTime, self.numberOfProfile, self.coordinateSeries

    def show_info(self):
        None

    def get_log(self):
        None


class Statistic:
    def __init__(self, datas=None, vel_data=None, echo_data=None):
        self.__vel_data = np.array(datas.vel_table if datas else vel_data)
        self.__echo_data = np.array(datas.echoTable if datas else echo_data)

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
    def __init__(self, datas=None, vel_data=None, sample_time=None, nprofile=None, coordinate_series=None):
        self.__vel_data = np.array(datas.vel_table if datas else vel_data)
        self.__sample_time = np.array(datas.sampleTime if datas else sample_time)
        self.__number_of_profile = np.array(datas.numberOfProfile if datas else nprofile)
        self.__coordinate_series = np.array(datas.coordinateSeries if datas else coordinate_series)

        self.__cylinder_r = None
        self.__delta_y = None

    # Update the variable self.__coordinate_series to store the data in the radial coordinate system.
    # If you don't execute these two functions, the variable will store the coordinates in the xi coordinate system.
    # Running this function will modify the data in self.__coordinate_series to represent the coordinates in the radial coordinate system.
    def outer_cylinder_dimensions(self, cylinder_r, wall_coordinates_xi, delta_y):
        self.__cylinder_r = None
        length_in_cylinder_in_axis_xi = np.sqrt(cylinder_r ** 2 - delta_y ** 2)

        # Update the variable self.__coordinate_series
        self.__coordinate_series = np.sqrt((length_in_cylinder_in_axis_xi - abs(
            wall_coordinates_xi - self.__coordinate_series)) ** 2 + delta_y ** 2)

    def inner_cylinder_dimensions(self, cylinder_r, wall_coordinates_xi, delta_y):
        None

    def do_fft(self, derivative_smoother_factor_1=7, derivative_smoother_factor_2=1):
        my_axis = 0
        fft_result = np.fft.rfft(self.__vel_data, axis=my_axis)
        magnitude = np.abs(fft_result) / self.__number_of_profile
        max_magnitude_indices = np.argmax(magnitude, axis=my_axis)
        max_magnitude = np.abs(fft_result[max_magnitude_indices, range(fft_result.shape[1])])
        phase_delay = np.angle(fft_result[max_magnitude_indices, range(fft_result.shape[1])])
        derivative_smoother_factor = [derivative_smoother_factor_1, derivative_smoother_factor_2]
        phase_delay_derivative = Tools.derivative(phase_delay, self.__coordinate_series, derivative_smoother_factor)
        real_part = fft_result[max_magnitude_indices, range(fft_result.shape[1])].real
        imag_part = fft_result[max_magnitude_indices, range(fft_result.shape[1])].imag

        return max_magnitude, phase_delay, phase_delay_derivative, real_part, imag_part

    def calculate_effective_shear_rate(self):
        _, _, _, real_part, imag_part = self.do_fft(derivative_smoother_factor=OFF)
        real_part_derivative = np.gradient(real_part, self.__coordinate_series)
        imag_part_derivative = np.gradient(imag_part, self.__coordinate_series)

    def doanaylsis(self):
        None


data = ReadData(r'C:\Users\ZHENG WENQING\Desktop\UVPReader\UVPdatas\0.5hz90deg.mfprof')
# file_data = ReadData(r'E:\Zheng\20230320\60rpm0003.mfprof')
FFTresult = data.analysis.do_fft()

# times = file_data.sampleTime
# coordinates = file_data.coordinate_series
