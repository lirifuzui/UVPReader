import re
uvp_parameter = ['Frequency=4000000\n', 'StartChannel=5.005\n', 'ChannelDistance=1.43\n', 'ChannelWidth=1.43\n', 'MaximumDepth=5855.85\n', 'SoundSpeed=2860\n', 'Angle=90\n', 'GainStart=5\n', 'GainEnd=9\n', 'Voltage=150\n', 'Iterations=32\n', 'NoiseLevel=0\n', 'CyclesPerPulse=4\n', 'TriggerMode=0\n', 'TriggerModeName=None\n', 'ProfileLength=158\n', 'ProfilesPerBlock=1024\n', 'Blocks=2048\n', 'AmplitudeStored=0\n', 'DoNotStoreDoppler=0\n', 'RawDataMin=-128\n', 'RawDataMax=127\n', 'RawDataRange=256\n', 'AmplDataMin=-8192\n', 'AmplDataMax=8191\n', 'VelocityInterpretingMode=0\n', 'UserSampleTime=1\n', 'SampleTime=500\n', 'UseMultiplexer=1\n', 'FlowMapping=0\n', 'FirstValidChannel=0\n', 'LastValidChannel=157\n', 'FlowRateType=0\n', 'PeriodEnhOffset=0\n', 'PeriodEnhPeriod=10\n', 'PeriodEnhNCycles=4294967295\n', "Comment=Data of transducer #9 from 'C:\\Documents and Settings\\Yanagisawa\\uvp101805tr.mfprof' file\\\n", "Data of transducer #9 from 'C:\\Documents and Settings\\Yanagisawa\\uvp101804mg.mfprof' file\\\n", "Data of transducer #9 from 'C:\\Documents and Settings\\Yanagisawa\\uvp101803trmg.mfprof' file\\\n", "Data of transducer #9 from 'C:\\Documents and Settings\\Yanagisawa\\uvp101802.mfprof' file\\\n", "Data of transducer #4 from 'C:\\Documents and Settings\\Yanagisawa\\uvp101801tr.mfprof' file\\\n", '\n', 'MeasurementProtocol=\n']
foot_parameters_values = []
flag = 0
for i, value in enumerate(uvp_parameter):
    if 'Comment=' in value:
        flag = 1
        start = i
        print(start)
    if flag == 0:
        foot_parameters_values.append(re.search(r"=(.*)\n", value).group(1))
    if 'MeasurementProtocol=' in value:
        comment = "".join(uvp_parameter[start:i-1])
        print(i)
        print(comment)
        foot_parameters_values.append(re.search(r"=(.*)", comment).group(1))
        foot_parameters_values.append(re.search(r"=(.*)\n", value).group(1))