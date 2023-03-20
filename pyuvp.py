from struct import unpack
import numpy as np

import Tools

ON = 1
OFF = 0


class ReadData:

    def __init__(self, file_path, read_as_mux=OFF):
        self.__measurement_info = {}
        self.__mux_config_params = {}

        # Velocity data and echo data may be two-dimensional arrays or three-dimensional arrays.
        # 如果没有开多传感器的话存在这里，是一个numpy的二维数组
        self.__vel_data = None
        self.__echo_data = None
        self.__time_series = None
        self.__coordinate_series = None
        # 如果开了多传感器的话存在这里，是一个一维列表，里面的每一项对应一个传感器的数据，是一个numpy的二维数组。
        self.__mux_vel_data_list = None
        self.__mux_echo_data_list = None
        self.__mux_time_series_list = None
        self.__mux_coordinate_series_list = None

        self.__read_data(file_path)

        self.statistic = Statistic(None, self.__vel_data, self.__echo_data, self.__time_series,
                                   self.__coordinate_series)

        print(self.__mux_config_params)

    def __read_params_part_I(self, uvp_datafile) -> None:
        # Read parameter information at the beginning of the file.
        # The data structure is as follows:
        """signum, c char [64]
        measParamsOffset1, c unsigned long
        measParamsOffset2", c unsigned long
        nProfiles, c unsigned long
        reserved1, c unsigned long
        flags, c unsigned long
        recordsize, c unsigned long
        nChannels, c unsigned long
        reserved2, c unsigned long
        startTime1, c unsigned long
        startTime2, c unsigned long """

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
        # Divide the data list into two lists, 'uvp_operational_params_list' and 'mux_config_params_list'.
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
            self.__mux_vel_data_list = [[]] * int(self.__mux_config_params['Table'])
            self.__mux_echo_data_list = [[]] * int(self.__mux_config_params['Table'])
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
            self.__time_series = [n * self.__measurement_info['SampleTime'] * 0.001 for n in
                                  range(self.__measurement_info['NumberOfProfiles'])]
        self.__coordinate_series = [
            self.__measurement_info['StartChannel'] + n * self.__measurement_info['ChannelDistance']
            for n in range(self.__measurement_info['NumberOfChannels'])]

    def __times_and_coordinates(self):
        self.__time_series = [n * self.__measurement_info['SampleTime'] * 0.001 for n in
                              range(self.__measurement_info['NumberOfProfiles'])]
        self.__coordinate_series = [self.__measurement_info['StartChannel'] + n * self.__measurement_info['ChannelDistance']
                                    for n in range(self.__measurement_info['NumberOfChannels'])]

    def __read_data(self, file_path) -> None:
        with open(file_path, 'rb') as uvpDatafile:
            self.__read_params_part_I(uvpDatafile)
            self.__read_params_part_II(uvpDatafile)

            # read velocity data and echo data
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
        # Resolution the velocity data, echo data, time series and coordinate series.
        self.resetSoundSpeed(self.__measurement_info['SoundSpeed'])

    @property
    def mux_state(self):
        return self.__measurement_info['UseMultiplexer']

    @property
    def echo_table(self):
        return self.__mux_echo_data_list if self.mux_state else self.__echo_data

    @property
    def vel_table(self):
        return self.__mux_vel_data_list if self.mux_state else self.__vel_data

    @property
    def time_series(self):
        return self.__time_series

    @property
    def coordinate_series(self):
        return self.__coordinate_series

    @property
    def summary_data(self):
        return self.__vel_data, self.__echo_data, self.__time_series, self.__coordinate_series
    
    @property
    def return_raw_data(self):
        return self.__raw_vel_data

    def show_info(self):
        None

    def get_log(self):
        None


class Statistic:
    def __init__(self, datas=None, vel_data=None, echo_data=None, times=None, coordinates=None):
        self.__vel_data = np.array(datas.vel_table if datas else vel_data)
        self.__echo_data = np.array(datas.echo_table if datas else echo_data)
        self.__times = np.array(datas.time_series if datas else times)
        self.__coordinates = np.array(datas.coordinate_series if datas else coordinates)

    # Return the average, maximum, and minimum values of the speed at different positions.
    # The structure is three one-dimensional arrays.
    @property
    def vel_average(self):
        vel_average = np.mean(self.__vel_data, axis=0)
        vel_max = np.max(self.__vel_data, axis=0)
        vel_min = np.min(self.__vel_data, axis=0)
        return vel_average, vel_max, vel_min

    def movvar(self):
        if isinstance(self.__vel_data[0][0], list):
            kernel = np.repeat(1.0, 3) / 3
            self.__movvar = np.array(
                [(np.array(signal_tdx_data) ** 2 - np.convolve(signal_tdx_data, kernel, 'valid') ** 2)
                 for signal_tdx_data in self.__vel_data])
        else:
            kernel = np.repeat(1.0, 3) / 3
            self.__movvar = np.array(self.__vel_data) ** 2 - np.convolve(self.__vel_data, kernel, 'valid') ** 2


class Analysis:
    def __init__(self, being_read_data):
        self.__data = being_read_data
        self.cutData = CutData(being_read_data)

    def FFT(self):
        None

    def doanaylsis(self):
        None


class CutData:
    def __init__(self, being_read_data):
        self.__data = being_read_data

    def from_time(self, min_index, max_index):
        if self.__data.vel_table.ndim == 3:
            return self.__data.vel_table[:, min_index:max_index, :]
        else:
            return self.__data.vel_table[min_index:max_index, :]

    def from_coordinate(self, min_coordinate, max_coordinate):
        None


#data = ReadData(r'UVPdatas/0.5hz150deg.mfprof')
data = ReadData(r'E:\Zheng\20230320\60rpm0003.mfprof')
vel_data = data.vel_table[0]
echo_data = data.echo_table[0]
velraw = data.return_raw_data
# times = data.time_series
# coordinates = data.coordinate_series

