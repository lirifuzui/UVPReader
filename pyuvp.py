from struct import unpack
from re import search

import numpy as np

import Tools

ON = 1
OFF = 0


class ReadData:

    def __init__(self, file_path, read_as_mux=OFF):
        self.__data_rw_params = {}
        self.__uvp_operational_params = {}
        self.__mux_config_params = {}

        # Velocity data and echo data may be two-dimensional arrays or three-dimensional arrays.
        # If the multiplexer is on, they will be stored as three-dimensional arrays.
        # The structure is [tdxs[times[position]]], or [times[position]]
        self.__vel_data = None
        self.__echo_data = None

        self.__time_series = None
        self.__coordinate_series = None

        self.__read_data(file_path, read_as_mux)

        self.statistic = Statistic(None, self.__vel_data, self.__echo_data, self.__time_series,
                                   self.__coordinate_series)

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
        head_datas = [unpack('L', uvp_datafile.read(4)) for _ in range(10)]
        self.__nums_profiles = int(head_datas[2][0])
        self.__flag = int(head_datas[4][0])
        self.__nums_channels = int(head_datas[6][0])

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
        index_2 = [i for i, line in enumerate(uvp_operational_params_list) if line.startswith('MeasurementProtocol=')][
            0]
        index_3 = [i for i, line in enumerate(mux_config_params_list) if line.startswith('Table=')][0]
        for item in uvp_operational_params_list[:index_1]:
            if not item:
                continue
            parts = item.split("=")
            name = parts[0].strip()
            value = None if parts[1].strip() == '' else parts[1].strip()
            if value.replace('.', '').replace('-', '').isdigit():
                value = float(value)
            self.__uvp_operational_params[name] = value
        comment_value = "\n".join(uvp_operational_params_list[index_1:index_2]).replace("Comment=", "")
        self.__uvp_operational_params["Comment"] = None if comment_value == '' else comment_value
        protocol_value = "\n".join(uvp_operational_params_list[index_2:]).replace("MeasurementProtocol=", "")
        self.__uvp_operational_params["MeasurementProtocol"] = None if protocol_value == '' else protocol_value

        for item in mux_config_params_list[:index_3+1]:
            if not item:
                continue
            parts = item.split("=")
            name = parts[0].strip()
            value = None if parts[1].strip() == '' else parts[1].strip()
            if value.replace('.', '').replace('-', '').isdigit():
                value = float(value)
            self.__mux_config_params[name] = value
        mux_config = [list(map(float, item.split())) for item in mux_config_params_list[index_3+1:]]
        self.__mux_config_params['MultiplexerConfiguration'] = mux_config
        print(self.__uvp_operational_params)

    def reset_soundspeed(self, sound_speed, read_as_mux) -> None:
        self.__uvp_operational_params['SoundSpeed'] = sound_speed
        max_depth = self.__uvp_operational_params['MaximumDepth']
        doppler_coefficient = sound_speed / (max_depth * 2.0) / 256.0 * 1000.0
        sounds_speed_coefficient = sound_speed / (self.__uvp_operational_params['Frequency'] * 2.0)

        if self.__uvp_operational_params['UseMultiplexer'] and read_as_mux:
            '''nums_tdx = self.__number_of_tdxs_on
            nums_cycles_is_on = 0
            online_tdx_list = []
            for tdx in range(nums_tdx):
                if self.__mux_config[tdx][0]:
                    nums_cycles_is_on += self.__mux_config[tdx][2]
                    for _ in range(self.__mux_config[tdx][2]):
                        online_tdx_list.append(tdx)
            slice_range = slice(None, self.__nums_profiles, nums_cycles_is_on)
            vel_resolution = doppler_coefficient * sounds_speed_coefficient * 1000 * 1.0 / np.sin(
                self.__mux_config[online_tdx_list[0]][3] * np.pi / 180)
            self.__vel_data = self.__raw_vel_data[slice_range] * vel_resolution
            self.__vel_data = self.__vel_data.transpose((0, 2, 1))
            self.__echo_data = self.__raw_echo_data[slice_range]
            self.__echo_data = self.__echo_data.transpose((0, 2, 1))'''
            None
        else:
            angle_coefficient = 1.0 / np.sin(self.__uvp_operational_params['Angle'] * np.pi / 180)
            vel_resolution = doppler_coefficient * sounds_speed_coefficient * 1000 * angle_coefficient
            self.__vel_data = self.__raw_vel_data * vel_resolution
            self.__echo_data = self.__raw_echo_data

    def __times_and_coordinates(self):
        self.__time_series = [n * self.__uvp_operational_params['UserSampleTime'] * 0.001 for n in range(self.__nums_profiles)]
        self.__coordinate_series = [self.__uvp_operational_params['StartChannel'] + n * self.__uvp_operational_params['ChannelDistance']
                                    for n in range(self.__nums_channels)]

    def __read_data(self, file_path, read_as_mux) -> None:
        with open(file_path, 'rb') as uvpDatafile:
            self.__read_params_part_I(uvpDatafile)
            self.__read_params_part_II(uvpDatafile)

            # read velocity data and echo data
            self.__raw_vel_data = np.zeros((self.__nums_profiles, self.__nums_channels))
            self.__raw_echo_data = np.zeros((self.__nums_profiles, self.__nums_channels))
            uvpDatafile.seek(104)
            for i in range(self.__nums_profiles):
                uvpDatafile.seek(16, 1)
                encode_vel_data = uvpDatafile.read(self.__nums_channels * 2)
                datatype = '{}h'.format(self.__nums_channels)
                self.__raw_vel_data[i] = unpack(datatype, encode_vel_data)
                if self.__flag:
                    encode_echo_data = uvpDatafile.read(self.__nums_channels * 2)
                    self.__raw_echo_data[i] = unpack(datatype, encode_echo_data)

        # Calculate the time and coordinates.
        self.__times_and_coordinates()
        # Resolution the velocity data.
        self.reset_soundspeed(self.__sound_speed)

    @property
    def mux_state(self):
        return self.__use_multiplexer

    @property
    def echo_table(self):
        return self.__echo_data

    @property
    def vel_table(self):
        return self.__vel_data

    @property
    def time_series(self):
        return self.__time_series

    @property
    def coordinate_series(self):
        return self.__coordinate_series

    @property
    def summary_data(self):
        return self.__vel_data, self.__echo_data, self.__time_series, self.__coordinate_series

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
        self.cutdata = CutData(being_read_data)

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


# data = ReadData(r'UVPdatas/0.5hz150deg.mfprof')
data = ReadData(r"C:\Users\zheng\Desktop\UVPopener_64bit\UVPopener\uvp073008.mfprof")
vel_data = data.vel_table
echo_data = data.echo_table
times = data.time_series
coordinates = data.coordinate_series
average = data.statistic.vel_average[0]
