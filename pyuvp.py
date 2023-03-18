from struct import unpack
from re import search

import numpy as np

import Tools


class ReadData:

    def __init__(self, file_path, threshold=1):
        # Velocity data and echo data may be two-dimensional arrays or three-dimensional arrays.
        # If the multiplexer is on, they will be stored as three-dimensional arrays.
        # The structure is [tdxs[times[position]]], or [times[position]]
        self.__vel_data = None
        self.__echo_data = None

        self.__time_series = None
        self.__coordinate_series = None

        self.__path = file_path
        self.__th = threshold
        self.__read_data()

        self.statistic = Statistic(None, self.__vel_data, self.__echo_data, self.__time_series,
                                   self.__coordinate_series)

    def __read_params_part_I(self, uvp_datafile) -> None:
        # Read parameter information at the beginning of the file.
        # The data structure is as follows:
        """ signum, c char [64]
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
        # Divide the data list into two lists, 'uvp parameter' and 'multiplexer parameter'.
        index = lines.index(b'[MUX_PARAMETER]\n')
        temp_uvp_params = lines[:index]
        del temp_uvp_params[0]
        temp_mux_params = lines[index + 1:]
        uvp_params = [value.decode('utf-8', errors='replace') for value in temp_uvp_params]
        mux_params = [value.decode('utf-8', errors='replace') for value in temp_mux_params]
        foot_parameters_values = []

        '''# To process the data of ‘uvp_parameter’, ‘Comment’ item needs to be raised separately
        for i, value in enumerate(uvp_params):
            if 'Comment=' in value:
                flag = 1
                begin_location = i
            if flag == 0:
                foot_parameters_values.append(search(r"=(.*)\n", value).group(1))
            if 'MeasurementProtocol=' in value:
                comment = "".join(uvp_params[begin_location:i - 1])
                temp_comment = comment.split("\n")
                comment = []
                for n in temp_comment:
                    str_comment = search("Comment=(.*)", n)
                    if str_comment is not None:
                        comment.append(str_comment.group(1))
                        continue
                    comment.append(n)
                nums_comment = len(comment)
                foot_parameters_values.append(nums_comment)
                foot_parameters_values.append(search(r"=(.*)\n", value).group(1))'''
        # To process the data of ‘uvp_parameter’, 'Comment' can be ignored
        for value in uvp_params:
            if 'Comment=' in value:
                break
            foot_parameters_values.append(search(r"=(.*)\n", value).group(1))

        # To process the data of ‘mux_parameter’, ‘Table’ item needs to be raised separately
        begin_location = 0
        mux_parameters_values = []
        for i, value in enumerate(mux_params):
            if 'Table=' in value:
                if '\\\n' in value:
                    mux_parameters_values.append(search(r"=(.*)\\\n", value).group(1))
                else:
                    mux_parameters_values.append(search(r"=(.*)\n", value).group(1))
                begin_location = i
                break
            mux_parameters_values.append(search(r"=(.*)\n", value).group(1))
        table = mux_params[begin_location + 1:]
        tdx_table = []
        for tdx in table:
            if '\\\n' in tdx:
                tdx = tdx.replace('\\\n', '')
            else:
                tdx = tdx.replace('\n', '')
            tdx_temp = tdx.split(' ')
            del tdx_temp[0]
            tdx_list = [int(x) for x in tdx_temp]
            tdx_table.append(tdx_list)

        self.__frequency = int(foot_parameters_values[0])
        self.__start_channel = float(foot_parameters_values[1])
        self.__channel_distance = float(foot_parameters_values[2])
        # self.__ChannelWidth = float(foot_parameters_values[3])
        self.__max_depth = float(foot_parameters_values[4])
        self.__sound_speed = int(foot_parameters_values[5])
        self.__angle = int(foot_parameters_values[6])
        self.__raw_data_min = int(foot_parameters_values[20])
        self.__raw_data_max = int(foot_parameters_values[21])
        self.__sample_time = int(foot_parameters_values[27])
        self.__use_multiplexer = int(foot_parameters_values[28])

        self.__nums_cycles = int(mux_parameters_values[0])
        self.__delay = int(mux_parameters_values[1])
        self.__nums_set = int(mux_parameters_values[3])
        self.__table = tdx_table

    def reset_soundspeed(self, sound_speed) -> None:
        self.__sound_speed = sound_speed
        max_depth = self.__max_depth * 2.0
        doppler_coefficient = sound_speed / max_depth / 256.0 * 1000.0
        sounds_speed_coefficient = sound_speed / (self.__frequency * 2.0)

        if self.__use_multiplexer:
            '''nums_tdx = self.__nums_set
            nums_cycles_is_on = 0
            online_tdx_list = []
            for tdx in range(nums_tdx):
                if self.__table[tdx][0]:
                    nums_cycles_is_on += self.__table[tdx][2]
                    for _ in range(self.__table[tdx][2]):
                        online_tdx_list.append(tdx)
            slice_range = slice(None, self.__nums_profiles, nums_cycles_is_on)
            vel_resolution = doppler_coefficient * sounds_speed_coefficient * 1000 * 1.0 / np.sin(
                self.__table[online_tdx_list[0]][3] * np.pi / 180)
            self.__vel_data = self.__raw_vel_data[slice_range] * vel_resolution
            self.__vel_data = self.__vel_data.transpose((0, 2, 1))
            self.__echo_data = self.__raw_echo_data[slice_range]
            self.__echo_data = self.__echo_data.transpose((0, 2, 1))'''
            None
        else:
            angle_coefficient = 1.0 / np.sin(self.__angle * np.pi / 180)
            vel_resolution = doppler_coefficient * sounds_speed_coefficient * 1000 * angle_coefficient
            self.__vel_data = self.__raw_vel_data * vel_resolution
            self.__echo_data = self.__raw_echo_data

    def __times_and_coordinates(self):
        self.__time_series = [n * self.__sample_time * 0.001 for n in range(self.__nums_profiles)]
        self.__coordinate_series = [self.__start_channel + n * self.__channel_distance for n in
                                    range(self.__nums_channels)]

    def __read_data(self) -> None:
        with open(self.__path, 'rb') as uvpDatafile:
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

        '''# Overflow treatment.
        if self.__th != 0:
            th_max = self.__th * self.__raw_data_max
            th_min = self.__th * self.__raw_data_min
            self.__raw_vel_data[(self.__th > 0) & (self.__raw_vel_data > th_max)] \
                -= self.__raw_data_max - self.__raw_data_min
            self.__raw_vel_data[(self.__th < 0) & (self.__raw_vel_data < th_min)] \
                += self.__raw_data_min - self.__raw_data_max
        self.__raw_echo_data[(self.__raw_echo_data < 0) | (self.__raw_echo_data > 500)] = 0'''

        self.reset_soundspeed(self.__sound_speed)

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


data = ReadData(r'UVPdatas/0.5hz150deg.mfprof')
vel_data = data.vel_table
echo_data = data.echo_table
times = data.time_series
coordinates = data.coordinate_series
average = data.statistic.vel_average[0]
