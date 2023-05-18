from struct import unpack

import numpy as np

import pyuvp

ON = 1
OFF = 0


class FileException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{self.message}"


class readData:
    def __init__(self, file_path):
        # To store the important UVP configuration parameters
        self.__measurement_info = {}
        self.__mux_config_params = {}

        # If the sound speed needs to be changed, the new sound speed is stored here.
        self.__new_sound_speed = None

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


    # Redefine the speed of sound and modify the data.
    def redefineSoundSpeed(self, new_sound_speed) -> None:
        self.__new_sound_speed = new_sound_speed
        sound_speed = self.__measurement_info['SoundSpeed']
        max_depth = self.__measurement_info['MaximumDepth']
        doppler_coefficient = sound_speed / (max_depth * 2.0) / 256.0 * 1000.0
        sounds_speed_coefficient = new_sound_speed / (self.__measurement_info['Frequency'] * 2.0)

        # Modifies the velocity and echo data according to the newly defined sound speed.

        # 这段代码中时间序列没弄好，
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
                                          'ChannelDistance'] - self.__measurement_info['ChannelDistance'] * 0.5,
                                      self.__measurement_info['ChannelDistance']) * (new_sound_speed / sound_speed)
        if int(self.__mux_config_params['Table']):
            self.__coordinate_series_list = [coordinate_series for _ in range(int(self.__mux_config_params['Table']))]
        else:
            self.__coordinate_series_list.append(coordinate_series)

    def __read_data(self, file_path) -> None:
        with open(file_path, 'rb') as uvpDatafile:
            try:
                self.__read_params_part_I(uvpDatafile)
                self.__read_params_part_II(uvpDatafile)
                # read velocity file_data and echo_data file_data
                self.__raw_vel_data = np.zeros((self.__measurement_info['NumberOfProfiles'],
                                                self.__measurement_info['NumberOfChannels']))
                self.__raw_echo_data = np.zeros((self.__measurement_info['NumberOfProfiles'],
                                                 self.__measurement_info['NumberOfChannels']))
            except np.core._exceptions._ArrayMemoryError:
                raise FileException("'.mfprof' file may be corrupted or altered."
                                    "'Number of Profiles' and 'Number of Channels' are beyond normal limits.")
            uvpDatafile.seek(104)
            for i in range(self.__measurement_info['NumberOfProfiles']):
                uvpDatafile.seek(16, 1)
                if self.__measurement_info['DoNotStoreDoppler'] != 1:
                    encode_vel_data = uvpDatafile.read(self.__measurement_info['NumberOfChannels'] * 2)
                    datatype = '{}h'.format(self.__measurement_info['NumberOfChannels'])
                    self.__raw_vel_data[i] = unpack(datatype, encode_vel_data)
                if self.__measurement_info['AmplitudeStored']:
                    encode_echo_data = uvpDatafile.read(self.__measurement_info['NumberOfChannels'] * 2)
                    self.__raw_echo_data[i] = unpack(datatype, encode_echo_data)

        # Resolution the velocity file_data, echo_data file_data, time series and coordinate series.
        self.redefineSoundSpeed(self.__measurement_info['SoundSpeed'])

    def createUSRAnalysis(self, tdx_num=0, ignoreException=False):
        return pyuvp.usr.Analysis(tdx_num=tdx_num, vel_data=self.velTables, time_series=self.timeSeries,
                                  coordinate_series=self.coordinateSeries, ignoreException=ignoreException)

    @property
    def muxStatus(self):
        return 'On' if self.__measurement_info['UseMultiplexer'] else 'OFF'

    @property
    def velTables(self):
        # velocity _mm/s
        return self.__vel_data_list

    @property
    def echoTables(self):
        return self.__echo_data_list

    @property
    def timeSeries(self):
        # time _s
        return self.__time_series_list

    @property
    def coordinateSeries(self):
        # coordinate _mm
        return self.__coordinate_series_list

    def show_info(self):
        None

    def get_log(self):
        None
