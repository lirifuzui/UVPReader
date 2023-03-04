from ctypes import *


# Definition of structure base on python.ctypes.Structure.
# structure of Duo Parameter at the head of data file.
class HeadParameter(Structure):
    head_parameters_format_string = "64sLLLLLLLLLL"
    _fields_ = [("signum", c_char * 64),
                # unsigned __int64 measParamsOffset
                # because unsignedlonglong cannot be used in this ver.
                ("measParamsOffset1", c_ulong),
                ("measParamsOffset2", c_ulong),
                ("nProfiles", c_ulong),
                ("reserved1", c_ulong),
                ("flags", c_ulong),
                ("recordsize", c_ulong),
                ("nChannels", c_ulong),
                ("reserved2", c_ulong),
                # unsigned __int64 startTime
                ("startTime1", c_ulong),
                ("startTime2", c_ulong)]

    def show(self):
        text = (f'Duo Parameter at the head of data file: \n'
                f'---------------------------------------------\n'
                f'{self.signum.decode()}'
                f'ParameterName\tType\tValue\n'
                f'---------------------------------------------\n')
        params = [('measParamsOffset1', 'unsignedlong', str(self.measParamsOffset1)),
                  ('measParamsOffset2', 'unsignedlong', str(self.measParamsOffset2)),
                  ('nProfiles', 'unsignedlong', str(self.nProfiles)),
                  ('reserved1', 'unsignedlong', str(self.reserved1)),
                  ('flags', 'unsignedlong', str(self.flags)),
                  ('recordsize', 'unsignedlong', str(self.recordsize)),
                  ('nChannels', 'unsignedlong', str(self.nChannels)),
                  ('reserved2', 'unsignedlong', str(self.reserved2)),
                  ('startTime1', 'unsignedlong', str(self.startTime1)),
                  ('startTime2', ' unsignedlong ', str(self.startTime2))]
        for name, type, value in params:
            text += f'{name}\t{type}\t{value}\n'
        text += (f'---------------------------------------------\n'
                 f'use "[your instantiated DataName].headparam.[Change to ParameterName]" to call the variables')
        print(text)
        return text


class FootParameter(Structure):
    _fields_ = [("Frequency", c_int),
                ("StartChannel", c_double),
                ("ChannelDistance", c_double),
                ("ChannelWidth", c_double),
                ("MaximumDepth", c_double),
                ("SoundSpeed", c_int),
                ("Angle", c_int),
                ("GainStart", c_ulong),
                ("GainEnd", c_ulong),
                ("Voltage", c_ulong),
                ("Iterations", c_ulong),
                ("NoiseLevel", c_ulong),
                ("CyclesPerPulse", c_ulong),
                ("TriggerMode", c_ulong),
                ("TriggerModeName", c_ulong),
                ("ProfileLength", c_ulong),
                ("ProfilesPerBlock", c_ulong),
                ("Blocks", c_ulong),
                ("AmplitudeStored", c_ulong),
                ("DoNotStoreDoppler", c_ulong),
                ("RawDataMin", c_int),
                ("RawDataMax", c_int),
                ("RawDataRange", c_ulong),
                ("AmplDataMin", c_ulong),
                ("AmplDataMax", c_ulong),
                ("VelocityInterpretingMode", c_ulong),
                ("UserSampleTime", c_ulong),
                ("SampleTime", c_int),
                ("UseMultiplexer", c_int),
                ("FlowMapping", c_bool),
                ("FirstValidChannel", c_ulong),
                ("LastValidChannel", c_ulong),
                ("FlowRateType", c_bool),
                ("PeriodEnhOffset", c_ulong),
                ("PeriodEnhPeriod", c_ulong),
                ("PeriodEnhNCycles", c_ulong),
                ("Comment", c_char * 1024),
                ("MeasurementProtocol", c_ulong)]


class MultiplexerParameter(Structure):
    _fields_ = [("nCycles", c_ulong),
                ("Delay", c_ulong),
                ("Version", c_ulong),
                ("nSet", c_int),
                ("Table", c_int *64 * 9)]
