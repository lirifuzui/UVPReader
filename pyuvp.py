from struct import unpack
from re import search
import numpy as np


class ReadData:
    def __init__(self, file_path, threshold=1):
        self.__vel_data = None
        self.__echo_data = None
        self.__new_sound_speed = None
        self.__time_series = None
        self.__position_series = None
        self.__coordinate_series = None

        self.__path = file_path
        self.__th = threshold
        self.__read_data()

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

    def __times_and_coordinates(self):
        self.__time_series = [n*self.__sample_time*0.001 for n in range(self.__nums_profiles)]
        self.__coordinate_series = [self.__start_channel + n*self.__channel_distance for n in range(self.__nums_channels)]

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

        # Overflow treatment.
        if self.__th > 0:
            self.__raw_vel_data[self.__raw_vel_data > self.__th * self.__raw_data_max] \
                = self.__raw_vel_data[self.__raw_vel_data > self.__th * self.__raw_data_max] \
                  - self.__raw_data_max + self.__raw_data_min
        if self.__th < 0:
            self.__raw_vel_data[self.__raw_vel_data < self.__th * self.__raw_data_min] \
                = self.__raw_vel_data[self.__raw_vel_data < self.__th * self.__raw_data_min] \
                  - self.__raw_data_max + self.__raw_data_min
        self.__raw_echo_data[(self.__raw_echo_data < 0) | (self.__raw_echo_data > 500)] = 0

        self.resetsoundspeed(self.__sound_speed)

    def resetsoundspeed(self, new_sound_speed) -> None:
        if new_sound_speed != self.__sound_speed:
            self.__new_sound_speed = new_sound_speed

        doppler_coefficient = new_sound_speed / (self.__max_depth * 2.0) / 256.0 * 1000.0
        sounds_speed_coefficient = new_sound_speed / (self.__frequency * 2.0)

        self.__vel_data = []
        self.__echo_data = []
        if self.__use_multiplexer:
            nums_tdx = self.__nums_set
            nums_cycles_is_on = 0
            online_tdx_list = []
            for tdx in range(nums_tdx):
                if self.__table[tdx][0]:
                    nums_cycles_is_on += self.__table[tdx][2]
                    for _ in range(self.__table[tdx][2]):
                        online_tdx_list.append(tdx)
            for n in range(nums_cycles_is_on):
                temp_vel_list = []
                temp_echo_list = []
                angle_coefficient = 1.0 / np.sin(self.__table[online_tdx_list[n - 1]][3] * np.pi / 180)
                vel_resolution = doppler_coefficient * sounds_speed_coefficient * 1000 * angle_coefficient
                while n <= self.__nums_profiles - 1:
                    temp_vel_list.append(self.__raw_vel_data[n] * vel_resolution)
                    temp_echo_list.append(self.__raw_echo_data[n])
                    n += nums_cycles_is_on
                self.__vel_data.append(temp_vel_list)
                self.__echo_data.append(temp_echo_list)
        else:
            angle_coefficient = 1.0 / np.sin(self.__angle * np.pi / 180)
            vel_resolution = doppler_coefficient * sounds_speed_coefficient * 1000 * angle_coefficient
            self.__vel_data = self.__raw_vel_data * vel_resolution
            self.__echo_data = self.__raw_echo_data

    @property
    def showtdxinfo(self) -> None:
        None

    def show_echo_data(self):
        return self.__echo_data
    def show_vel_data(self):
        return self.__vel_data
    def show_times(self):
        return self.__time_series
    def show_coordinates(self):
        return self.__coordinate_series

    def showinfo(self):
        None

    def statistic(self):
        None

    def getlog(self):
        None

class Statistic:
    def __init__(self, being_read_data):
        self.__data = being_read_data

class Analysis:
    def __init__(self, being_read_data):
        self.__data = being_read_data

    def cutdata(self):
        None

    def FFT(self):
        None

    def doanaylsis(self):
        None


class CutData(Analysis):
    def __init__(self):
        None

    def fromtime(self):
        None

    def fromlocation(self):
        None


data = ReadData(r'E:\Zheng\20230316\1hz60deg.mfprof')
vel_data = data.show_vel_data()
echo_data = data.show_echo_data()
times = data.show_times()
coordinates = data.show_coordinates()
