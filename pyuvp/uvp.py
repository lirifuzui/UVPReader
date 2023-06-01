import os
from datetime import datetime
from struct import unpack

import numpy as np

import pyuvp


class FileException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{self.message}"


class readUvpFile:
    def __init__(self, file_path, is_output=False):
        """
        Reads the '.mfprof' file containing profile data and parameter values from 'MET-FLOW uvp for OptekFirmware'
        and stores them in an instance variable.

        Args:
            file_path (str): The path to the input file.
            is_output (bool): Flag indicating whether to enable output. Defaults to False.
        """
        # Defines the output files location.
        # If file_path is not a full path, write the output file to the "temp" folder.
        self.__is_output = is_output
        current_time = datetime.now()
        output_folder_name = current_time.strftime("%Y%m%d%H%M%S")
        self.__output_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/" + output_folder_name

        # To store the important UVP configuration parameters
        self.__measurement_info = {}
        self.__mux_config_params = {}

        # If the sound speed needs to be changed, the new sound speed is stored here.
        self.__new_sound_speed = None

        # Velocity, echo, and time series data are each stored in a list.
        # Each item in the list corresponds to data from a tdx.
        # Notice! When using mux, the time delay set by the user should be at least 200 ms due to signal output conversion.
        self.__vel_arr_tdxs = []
        self.__echo_arr_tdxs = []
        self.__time_arr_tdxs = []

        # Although the coordinate series of each tdx data is the same, it is still stored in a list for ease of use.
        # Each item of the list contains the same coordinate series.
        self.__coords_arr_tdxs = []

        # Run the "__read_data" function and store the data in the corresponding class variables.
        self.__read_data(file_path)

    def __output_files(self) -> None:
        """
        Output basic information about the UVP and save data to files.

        Writes the information to a file called "UVPconfig.txt". Additionally,
        if multiplexer is used, saves velocity and echo data for each multiplexer
        configuration to separate CSV files. Otherwise, saves data for a single TDX
        to CSV files.

        Returns:
            None
        """

        # Create the output directory
        os.mkdir(self.__output_path)

        def save_data_to_csv(data, filename):
            """
            Save the given data to a CSV file.

            Args:
                data (ndarray): The data to be saved.
                filename (str): The name of the output file.

            Returns:
                None
            """
            rows, cols = data.shape
            output_data = np.zeros((rows + 1, cols + 1), dtype=data.dtype)
            output_data[1:, 1:] = data
            output_data[0, 1:] = self.__coords_arr_tdxs[0]
            output_data[1:, 0] = self.__time_arr_tdxs[0]
            np.savetxt(os.path.join(self.__output_path, filename), output_data, delimiter=',')

        if self.__measurement_info['UseMultiplexer']:
            # Save data for each multiplexer configuration
            configs = self.__mux_config_params['MultiplexerConfiguration']
            for tdx_num, config in enumerate(configs):
                if config[0] == 1:
                    multiplexer_num = int(config[1])
                    save_data_to_csv(self.__vel_arr_tdxs[tdx_num],
                                     f"UVP_sourceData_multiplexer#{multiplexer_num}_vel_data.csv")
                    save_data_to_csv(self.__echo_arr_tdxs[tdx_num],
                                     f"UVP_sourceData_multiplexer#{multiplexer_num}_echo_data.csv")
        else:
            # Save data for a single TDX
            save_data_to_csv(self.__vel_arr_tdxs[0], "UVP_sourceData_singleTDX_vel_data.csv")
            save_data_to_csv(self.__echo_arr_tdxs[0], "UVP_sourceData_singleTDX_echo_data.csv")

    def __read_params_part_I(self, uvp_datafile) -> None:
        """
        Reads parameter information at the beginning of the file.

        The file structure is as follows:\n
        signum: line char [64]\n
        measParamsOffset1: line unsigned long\n
        measParamsOffset2: line unsigned long\n
        nProfiles: line unsigned long\n
        reserved1: line unsigned long\n
        flags: line unsigned long\n
        recordsize: line unsigned long\n
        nChannels: line unsigned long\n
        reserved2: line unsigned long\n
        startTime1: line unsigned long\n
        startTime2: line unsigned long\n
        """

        uvp_datafile.seek(64)
        head_params = [unpack('L', uvp_datafile.read(4)) for _ in range(10)]
        self.__measurement_info['NumberOfChannels'] = int(head_params[6][0])
        self.__measurement_info['NumberOfProfiles'] = int(head_params[2][0])

    def __read_params_part_II(self, uvp_datafile) -> None:
        """
        Reads parameter information at the bottom of the file.

        This includes 'UVP PARAMETER' and 'MUX PARAMETER' two parts.

        Args:
            uvp_datafile (file): The file object representing the UVP data file.

        Returns:
            None
        """

        # Seek to the beginning of the file and read its content
        uvp_datafile.seek(0)
        file_content = uvp_datafile.read()

        # Find the starting position of the 'UVP_PARAMETER' section
        uvp_params_begin = file_content.find(b"[UVP_PARAMETER]")
        uvp_datafile.seek(uvp_params_begin)
        lines = uvp_datafile.readlines()

        # Divide the file content into two lists: 'uvp_operational_params_list' and 'mux_config_params_list'
        index = lines.index(b'[MUX_PARAMETER]\n')
        uvp_operational_params_list = [item.decode('utf-8', errors='replace').strip() for item in lines[1:index]]
        mux_config_params_list = [item.decode('utf-8', errors='replace').strip().replace('\\', '') for item in
                                  lines[index + 1:]]

        # Find the indices of relevant sections in the lists
        index_1 = next(i for i, line in enumerate(uvp_operational_params_list) if line.startswith('Comment='))
        index_2 = next(
            i for i, line in enumerate(uvp_operational_params_list) if line.startswith('MeasurementProtocol='))
        index_3 = next(i for i, line in enumerate(mux_config_params_list) if line.startswith('Table='))

        def parse_params(param_list, value_type):
            """
            Parse the parameter list and convert values to the specified value type.

            Args:
                param_list (list): The list of parameter strings.
                value_type (type): The desired value type for the parameter values.

            Returns:
                dict: A dictionary containing the parameter names and their corresponding values.
            """
            params = {}
            for item in param_list:
                if not item:
                    continue
                parts = item.split("=")
                name = parts[0].strip()
                value = parts[1].strip()
                if value.replace('.', '').replace('-', '').isdigit():
                    value = value_type(value)
                params[name] = value
            return params

        # Update the measurement_info dictionary with parsed UVP operational parameters
        self.__measurement_info.update(parse_params(uvp_operational_params_list[:index_1], float))
        comment_value = "\n".join(uvp_operational_params_list[index_1:index_2]).replace("Comment=", "")
        self.__measurement_info["Comment"] = comment_value if comment_value else None
        protocol_value = "\n".join(uvp_operational_params_list[index_2:]).replace("MeasurementProtocol=", "")
        self.__measurement_info["MeasurementProtocol"] = protocol_value if protocol_value else None

        # Update the mux_config_params dictionary with parsed MUX configuration parameters
        self.__mux_config_params.update(parse_params(mux_config_params_list[:index_3 + 1], float))
        mux_config = [list(map(float, item.split())) for item in mux_config_params_list[index_3 + 1:]]
        self.__mux_config_params['MultiplexerConfiguration'] = mux_config

    # Redefine the speed of sound and modify the data.
    def defineSoundSpeed(self, new_sound_speed) -> None:
        self.__new_sound_speed = new_sound_speed
        sound_speed = self.__measurement_info['SoundSpeed']
        max_depth = self.__measurement_info['MaximumDepth']
        doppler_coefficient = sound_speed / (max_depth * 2.0) / 256.0 * 1000.0
        sounds_speed_coefficient = new_sound_speed / (self.__measurement_info['Frequency'] * 2.0)

        # Modifies the velocity and echo data according to the newly defined sound speed.

        # 这段代码中时间序列没弄好，
        if self.__measurement_info['UseMultiplexer']:
            self.__vel_arr_tdxs = [[] for _ in range(int(self.__mux_config_params['Table']))]
            self.__echo_arr_tdxs = [[] for _ in range(int(self.__mux_config_params['Table']))]
            self.__time_arr_tdxs = [[] for _ in range(int(self.__mux_config_params['Table']))]

            times = np.arange(0, self.__measurement_info['NumberOfProfiles'] *
                              self.__measurement_info['SampleTime'], self.__measurement_info['SampleTime'])
            time_plus = 0
            temp_vel_data = self.__raw_vel_arr
            temp_echo_data = self.__raw_echo_arr
            while list(temp_vel_data):
                now_index = 0
                for tdx in range(int(self.__mux_config_params['Table'])):
                    if self.__mux_config_params['MultiplexerConfiguration'][tdx][0]:
                        number_of_read_lines = int(self.__mux_config_params['MultiplexerConfiguration'][tdx][2])
                        self.__vel_arr_tdxs[tdx].extend(
                            temp_vel_data[now_index:now_index + number_of_read_lines])
                        self.__echo_arr_tdxs[tdx].extend(
                            temp_echo_data[now_index:now_index + number_of_read_lines])
                        now_index += number_of_read_lines
                        self.__time_arr_tdxs[tdx].extend(
                            times[now_index:now_index + number_of_read_lines] + time_plus)
                        if tdx + 1 < int(self.__mux_config_params['Table']):
                            time_plus += self.__mux_config_params['MultiplexerConfiguration'][tdx + 1][3]
                        else:
                            time_plus += self.__mux_config_params['MultiplexerConfiguration'][0][3]
                    else:
                        continue
                temp_vel_data = temp_vel_data[now_index:]
                temp_echo_data = temp_echo_data[now_index:]
                times = times[now_index:]
                time_plus += self.__mux_config_params['CycleDelay']
            self.__vel_arr_tdxs = [np.array(item) for item in self.__vel_arr_tdxs]
            self.__echo_arr_tdxs = [np.array(item) for item in self.__echo_arr_tdxs]

        else:
            angle_coefficient = 1.0 / np.sin(self.__measurement_info['Angle'] * np.pi / 180)
            vel_resolution = doppler_coefficient * sounds_speed_coefficient * 1000 * angle_coefficient
            vel_data = self.__raw_vel_arr * vel_resolution
            echo_data = self.__raw_echo_arr
            self.__vel_arr_tdxs.append(vel_data)
            self.__echo_arr_tdxs.append(echo_data)

            times = np.arange(0, self.__measurement_info['NumberOfProfiles'] *
                              self.__measurement_info['SampleTime'], self.__measurement_info['SampleTime'])
            self.__time_arr_tdxs.append(times * 0.001)

        # Store multiple coordinate series of tdx data into a list
        coordinate_series = np.arange(self.__measurement_info['StartChannel'], self.__measurement_info['StartChannel'] +
                                      self.__measurement_info['NumberOfChannels'] * self.__measurement_info[
                                          'ChannelDistance'] - self.__measurement_info['ChannelDistance'] * 0.5,
                                      self.__measurement_info['ChannelDistance']) * (new_sound_speed / sound_speed)
        if int(self.__mux_config_params['Table']):
            self.__coords_arr_tdxs = [coordinate_series for _ in range(int(self.__mux_config_params['Table']))]
        else:
            self.__coords_arr_tdxs.append(coordinate_series)

    def __read_data(self, file_path) -> None:
        try:
            uvpDatafile = open(file_path, 'rb')
        except FileNotFoundError:
            raise FileException("File not found.")
        try:
            self.__read_params_part_I(uvpDatafile)
            self.__read_params_part_II(uvpDatafile)
            # read velocity file_data and echo_data file_data
            self.__raw_vel_arr = np.zeros((self.__measurement_info['NumberOfProfiles'],
                                           self.__measurement_info['NumberOfChannels']))
            self.__raw_echo_arr = np.zeros((self.__measurement_info['NumberOfProfiles'],
                                            self.__measurement_info['NumberOfChannels']))
        except np.core._exceptions._ArrayMemoryError:
            raise FileException("'.mfprof' file may be corrupted or altered."
                                "'Number of Profiles' and 'Number of Channels' are beyond normal limits.")
        uvpDatafile.seek(104)
        datatype = '{}h'.format(self.__measurement_info['NumberOfChannels'])
        for i in range(self.__measurement_info['NumberOfProfiles']):
            uvpDatafile.seek(16, 1)
            if self.__measurement_info['DoNotStoreDoppler'] != 1:
                encode_vel_data = uvpDatafile.read(self.__measurement_info['NumberOfChannels'] * 2)
                self.__raw_vel_arr[i] = unpack(datatype, encode_vel_data)
            if self.__measurement_info['AmplitudeStored']:
                encode_echo_data = uvpDatafile.read(self.__measurement_info['NumberOfChannels'] * 2)
                self.__raw_echo_arr[i] = unpack(datatype, encode_echo_data)
        uvpDatafile.close()

        # Resolution the velocity file_data, echo_data file_data, time series and coordinate series.
        self.defineSoundSpeed(self.__measurement_info['SoundSpeed'])
        # Output Data.
        if self.__is_output is True:
            self.__output_files()

    def createUSRAnalysis(self, tdx_num=0, ignoreException=False):
        return pyuvp.usr.Analysis(tdx_num=tdx_num, vel_data=self.velTables, time_series=self.timeSeries,
                                  coordinate_series=self.coordinateSeries, ignoreException=ignoreException)

    @property
    def muxStatus(self):
        return 'On' if self.__measurement_info['UseMultiplexer'] else 'OFF'

    @property
    def velTables(self):
        # velocity _mm/s
        return self.__vel_arr_tdxs

    @property
    def echoTables(self):
        return self.__echo_arr_tdxs

    @property
    def timeSeries(self):
        # time _s
        return self.__time_arr_tdxs

    @property
    def coordinateSeries(self):
        # coordinate _mm
        return self.__coords_arr_tdxs

    @property
    def output_path(self):
        return self.__output_path
