import readuvpfiles

file = readuvpfiles.ReadMetFlowFiles("example_1.mfprof")
print(file.settings.nProfiles)
print(file.settings.nChannels)