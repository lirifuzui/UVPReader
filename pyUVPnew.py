from struct import unpack
from re import search


class ReadData:
    def __init__(self, file_path, threshold=1):
        self.__path = file_path
        self.__th = threshold
        self.__read_data()

    def __read_params_part_I(self, uvp_datafile):
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
        self.__nums_profiles = head_datas[2]
        self.__flag = head_datas[4]
        self.__nums_channels = [6]

    def __read_params_part_II(self, uvp_datafile):
        # Read parameter information at the bottom of the file.
        # Including 'UVP PARAMETER' and 'MUX PARAMETER' two parts.
        uvp_datafile.seek(0)
        foot_datas = uvp_datafile.read()
        uvp_params_begin = foot_datas.find(b"[UVP_PARAMETER]")
        foot_datas.seek(uvp_params_begin)
        lines = foot_datas.readlines()
        # Divide the data list into two lists, 'uvp parameter' and 'multiplexer parameter'.
        index = lines.index(b'[MUX_PARAMETER]\n')
        temp_uvp_params = lines[:index]
        del temp_uvp_params[0]
        temp_mux_params = lines[index + 1:]
        uvp_params = [value.decode('utf-8', errors='replace') for value in temp_uvp_params]
        mux_params = [value.decode('utf-8', errors='replace') for value in temp_mux_params]
        foot_parameters_values = []
        flag = 0

        # To process the data of ‘uvp_parameter’, ‘Comment’ item needs to be raised separately
        begin_location = None
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
                foot_parameters_values.append(search(r"=(.*)\n", value).group(1))

        # To process the data of ‘mux_parameter’, ‘Table’ item needs to be raised separately
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
        TDX_TABLE = []
        for TDX in table:
            if '\\\n' in TDX:
                TDX = TDX.replace('\\\n', '')
            else:
                TDX = TDX.replace('\n', '')
            tdx_temp = TDX.split(' ')
            del tdx_temp[0]
            tdx_list = [int(x) for x in tdx_temp]
            TDX_TABLE.append(tdx_list)
        temp_TDX_TABLE = TDX_TABLE.copy()
        for time in range(64 - len(temp_TDX_TABLE)):
            TDX_TABLE.append([0, 0, 0, 0, 0, 0, 0, 0, 0])
        # TDX_TABLE_tuple = tuple(TDX_TABLE)
        # 向结构体中赋值
        # 这不是个好方法，未来可以优化一下
        self._footparam.Frequency = int(foot_parameters_values[0])
        self._footparam.StartChannel = float(foot_parameters_values[1])
        self._footparam.ChannelDistance = float(foot_parameters_values[2])
        self._footparam.ChannelWidth = float(foot_parameters_values[3])
        self._footparam.MaximumDepth = float(foot_parameters_values[4])
        self._footparam.SoundSpeed = int(foot_parameters_values[5])
        self._footparam.Angle = int(foot_parameters_values[6])
        self._footparam.GainStart = int(foot_parameters_values[7])
        self._footparam.GainEnd = int(foot_parameters_values[8])
        self._footparam.RawDataMin = int(foot_parameters_values[20])
        self._footparam.RawDataMax = int(foot_parameters_values[21])
        self._footparam.SampleTime = int(foot_parameters_values[27])
        self._footparam.UseMultiplexer = int(foot_parameters_values[28])
        self._footparam.Comment = ''.join(comment)

        self._muxparam.nCycles = int(mux_parameters_values[0])
        self._muxparam.Delay = int(mux_parameters_values[1])
        self._muxparam.nSet = int(mux_parameters_values[3])
        self._muxparam.Table = TDX_TABLE
    def __read_data(self):
        with open(self.__path, 'rb') as uvpDatafile:
            self.__read_params_part_I(uvpDatafile)
            self.__read_params_part_II(uvpDatafile)

    def showinfo(self):
        None
    def statistic(self):
        None
    def getlog(self):
        None


class Analysis:
    def __init__(self, being_read_data):
        self._data = being_read_data
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

data = ReadData(r'C:\Users\zheng\Desktop\Silicon oil\15rpm.mfprof')