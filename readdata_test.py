import struct
import re
import numpy as np
from DuoParameters import *


class ReadData:
    def __init__(self, file_path, th=1):
        self.file_path = file_path  # file path
        self._headparam = None  # Initialize a structure variable,'HeadParameter'
        self._footparam = FootParameter  # Initialize a structure variable,'FootParameter'
        self._muxparam = MultiplexerParameter  # Initialize a structure variable,'MultiplexerParameter'
        self._th = th  # Thereshold for overflow treatment
        self._vel_data = None
        self._echo_data = None

        # Run the internal method, read the file
        self._read_data()
        self.showparam = self.ShowParam(self)

    # ----------------------------------------------------------------------------
    @property
    def headparam(self):
        return self._headparam

    @property
    def footparam(self):
        return self._footparam

    @property
    def muxparam(self):
        return self._muxparam

    @property
    def velarray(self):
        return np.array(self._vel_data)

    @property
    def echoarray(self):
        return np.array(self._echo_data)

    # ----------------------------------------------------------------------------
    def _read_data(self) -> None:
        with open(self.file_path, "rb") as f:
            # read parameters at head
            data = f.read(sizeof(HeadParameter))
            head_parameters_values = list(struct.unpack(HeadParameter.head_parameters_format_string, data))
            # Assign values to instantiated structure
            self._headparam = HeadParameter(*head_parameters_values)

            # read velocity data and echo data
            times = self._headparam.nProfiles
            positions = self._headparam.nChannels
            _raw_vel_data = np.zeros((times, positions))
            _raw_echo_data = np.zeros((times, positions))
            for i in range(self._headparam.nProfiles):
                f.seek(16, 1)
                data = f.read(2 * positions)
                datatype = '{}h'.format(positions)
                _raw_vel_data[i] = struct.unpack(datatype, data)
                if self._headparam.flags:
                    data = f.read(2 * positions)
                    _raw_echo_data[i] = struct.unpack(datatype, data)

            # read parameters at foot
            # Stored in a list named "lines" in binary format, containing two parts "UVP PARAMETER" and "[MUX PARAMETER]"
            f.seek(0)
            data = f.read()
            position = data.find(b"[UVP_PARAMETER]")
            f.seek(position)
            lines = f.readlines()
            # 把数据列表分成两个列表，一个是uvp parameter，另一个是multiplexer parameter
            index = lines.index(b'[MUX_PARAMETER]\n')
            temp_uvp_parameter = lines[:index]
            del temp_uvp_parameter[0]
            temp_multiplexer_parameter = lines[index + 1:]
            uvp_parameter = [value.decode('utf-8', errors='replace') for value in temp_uvp_parameter]
            multiplexer_parameter = [value.decode('utf-8', errors='replace') for value in temp_multiplexer_parameter]
            foot_parameters_values = []
            flag = 0

            # 处理一下 uvp_parameter 的数据，主要把Comment项单独提出来，其他都和head一样
            for i, value in enumerate(uvp_parameter):
                if 'Comment=' in value:
                    flag = 1
                    start = i
                if flag == 0:
                    foot_parameters_values.append(re.search(r"=(.*)\n", value).group(1))
                if 'MeasurementProtocol=' in value:
                    comment = "".join(uvp_parameter[start:i - 1])
                    temp_comment = comment.split("\n")
                    comment = []
                    for n in temp_comment:
                        str = re.search("Comment=(.*)", n)
                        if str != None:
                            comment.append(str.group(1))
                            continue
                        comment.append(n)
                    nComment = len(comment)
                    foot_parameters_values.append(nComment)
                    foot_parameters_values.append(re.search(r"=(.*)\n", value).group(1))

            mux_parameters_values = []
            for i, value in enumerate(multiplexer_parameter):
                if 'Table=' in value:
                    if '\\\n' in value:
                        mux_parameters_values.append(re.search(r"=(.*)\\\n", value).group(1))
                    else:
                        mux_parameters_values.append(re.search(r"=(.*)\n", value).group(1))
                    start = i
                    break
                mux_parameters_values.append(re.search(r"=(.*)\n", value).group(1))
            table = multiplexer_parameter[start + 1:]
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

            # Overflow treatment
            if self._th > 0:
                _raw_vel_data[_raw_vel_data > self._th * self._footparam.RawDataMax] \
                    = _raw_vel_data[_raw_vel_data > self._th * self._footparam.RawDataMax] \
                    - self._footparam.RawDataMax + self._footparam.RawDataMin
            if self._th < 0:
                _raw_vel_data[_raw_vel_data < self._th * self._footparam.RawDataMin] \
                    = _raw_vel_data[_raw_vel_data < self._th * self._footparam.RawDataMin] \
                    - self._footparam.RawDataMax + self._footparam.RawDataMin

            _raw_echo_data[(_raw_echo_data < 0) | (_raw_echo_data > 500)] = 0

            # 处理数据
            _doppler_coefficient = self._footparam.SoundSpeed / (self._footparam.MaximumDepth * 2.0) / 256.0 * 1000.0
            _sounds_speed_coefficient = self._footparam.SoundSpeed / (self._footparam.Frequency * 2.0)

            if self._footparam.UseMultiplexer:
                nTDX = self._muxparam.nSet
                nPinCycle = 0

                onlist = []
                for tdx in range(nTDX):
                    if self._muxparam.Table[tdx][0]:
                        nPinCycle += self._muxparam.Table[tdx][2]
                        for n in range(self._muxparam.Table[tdx][2]):
                            onlist.append(tdx)

                self._vel_data = []
                self._echo_data = []
                for n in range(nPinCycle):
                    veltemplist = []
                    echotemplist = []

                    AngleCoefficient = 1.0 / np.sin(self._muxparam.Table[onlist[n - 1]][3] * np.pi / 180)
                    VelResolustion = _doppler_coefficient * _sounds_speed_coefficient * 1000 * AngleCoefficient
                    while n <= self._headparam.nProfiles - 1:
                        veltemplist.append(_raw_vel_data[n] * VelResolustion)
                        echotemplist.append(_raw_echo_data[n])
                        n += nPinCycle
                    self._vel_data.append(veltemplist)
                    self._echo_data.append(echotemplist)
            else:
                AngleCoefficient = 1.0 / np.sin(self._footparam.Angle * np.pi / 180)
                VelResolustion = _doppler_coefficient * _sounds_speed_coefficient * 1000 * AngleCoefficient
                self._vel_data = _raw_vel_data * VelResolustion
                self._echo_data = _raw_echo_data

    class ShowParam:
        def __init__(self, readdata):
            self.readdata = readdata

        def head(self):
            None


# data = ReadData(r"C:/Users/zheng/Desktop/UVP/UVPopener_64bit/UVPopener/uvp073008.mfprof")
data = ReadData(r'C:\Users\zheng\Desktop\Silicon oil\15rpm.mfprof')
data.headparam.show()
vel = data.velarray
echo = data.echoarray
print(vel)
print(echo)
