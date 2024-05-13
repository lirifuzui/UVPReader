#include "ReadMetFlowFiles.h"

ReadMetFlowFiles::ReadMetFlowFiles(const std::string& file_path) : file_path(file_path) {
    readFile();
}

// 从FILETIME获取毫秒单位的时间
ULONGLONG ReadMetFlowFiles::FileTimeToMilliseconds(const FILETIME& ft) {
    ULARGE_INTEGER ull;
    ull.LowPart = ft.dwLowDateTime;
    ull.HighPart = ft.dwHighDateTime;
    return ull.QuadPart / 10000; // 100 nanoseconds to milliseconds
}

void ReadMetFlowFiles::readFile() {
    std::ifstream file(file_path, std::ios::binary);
    if (!file.is_open()) {
        std::cout << "Error" << std::endl;
        return;
    }

    // 读取文件的第一部分，File Header，存储在结构体变量settings中
        //创建一个内存缓冲区，用于储存临时数据，大小为104字节
        char buffer[104];
    //读取文件前104字节的数据
    file.read(buffer, sizeof(buffer));
    //解析数据，存入结构体变量settings中
    settings.signum = std::string(buffer, 64);
    settings.measParamsOffset = *reinterpret_cast<uint64_t*>(buffer + 64);
    settings.nProfiles = *reinterpret_cast<uint32_t*>(buffer + 72);
    settings.reserved1 = *reinterpret_cast<uint32_t*>(buffer + 76);
    settings.flags = *reinterpret_cast<uint32_t*>(buffer + 80);
    settings.recordSize = *reinterpret_cast<uint32_t*>(buffer + 84);
    settings.nChannels = *reinterpret_cast<uint32_t*>(buffer + 88);
    settings.reserved2 = *reinterpret_cast<uint32_t*>(buffer + 92);

    start_time = *reinterpret_cast<FILETIME*>(buffer + 96);
    FileTimeToSystemTime(&start_time, &settings.startTime);

    //判断这个文件中是否包含了速度数据和回声数据
    bool include_Doppler = true;
    bool include_Amplitude = true;
    if (settings.flags == 0) {
        include_Amplitude = false;
    }
    if (((settings.recordSize - 16) / settings.nChannels == 1) && include_Amplitude) {
        include_Doppler = false;
    }

    // 读取文件的第二部分，Profiles。
    int16_t doppler_value = 0;
    int16_t amplitude_value = 0;

    std::vector<int16_t> doppler_values_in_channels(settings.nChannels);
    std::vector<int16_t> amplitude_values_in_channels(settings.nChannels);

    ULONGLONG zero_time;

    for (size_t  i = 0; i < settings.nProfiles; ++i) {
        //读取Profile Header，数据存储在相应的容器中。
        file.read(buffer, sizeof(uint32_t) * 2 + sizeof(uint64_t));
        profile_status.push_back(*reinterpret_cast<uint32_t*>(buffer));
        profile_transducers.push_back(*reinterpret_cast<uint32_t*>(buffer + 4));

        if (i == 0) {
            zero_time = ReadMetFlowFiles::FileTimeToMilliseconds(*reinterpret_cast<FILETIME*>(buffer + 8));
            porfile_start_times.push_back(0);
        }
        else {
            porfile_start_times.push_back(ReadMetFlowFiles::FileTimeToMilliseconds(*reinterpret_cast<FILETIME*>(buffer + 8)) - zero_time);
        }

        // 清空通道数据
        doppler_values_in_channels.clear();
        amplitude_values_in_channels.clear();

        //开始循环读取Dopplerdata和Amplitudedata
        for (size_t i = 0; i < settings.nChannels; ++i) {
            if (include_Doppler) {
                file.read(reinterpret_cast<char*>(&doppler_value), sizeof(int16_t));
                doppler_values_in_channels.push_back(doppler_value);
            }
            if (include_Amplitude) {
                file.read(reinterpret_cast<char*>(&amplitude_value), sizeof(int16_t));
                amplitude_values_in_channels.push_back(amplitude_value);
            }
        }
        if (include_Doppler) {
            doppler_values.push_back(doppler_values_in_channels);
        }
        if (include_Amplitude) {
            amplitude_values.push_back(amplitude_values_in_channels);
        }
    }

    //读取文件的第三部分，Measurement parameters
    std::string line;
    std::string section;
    bool read_UVP_PARAMETER = false; // 标志，指示是否已经读取到了[UVP_PARAMETER]部分
    bool read_MUX_PARAMETER = false; // 标志，指示是否已经读取到了[MUX_PARAMETER]部分
    while (std::getline(file, line)) {
        std::istringstream iss(line);
        std::string key, value;
        if (line.empty()) continue; // 忽略空行
        size_t found = line.find("[UVP_PARAMETER]");
        if (found != std::string::npos) {
            read_UVP_PARAMETER = true; // 读取到了[UVP_PARAMETER]部分
            continue;
        }
        found = line.find("[MUX_PARAMETER]");
        if (found != std::string::npos) {
            read_MUX_PARAMETER = true; // 读取到了[MUX_PARAMETER]部分
            continue;
        }
        if (read_UVP_PARAMETER && !read_MUX_PARAMETER) {
            std::getline(iss, key, '=');
            std::getline(iss, value);
            if (key == "Frequency") settings.Frequency = std::stoul(value);
            else if (key == "StartChannel") settings.StartChannel = std::stod(value);
            else if (key == "ChannelDistance") settings.ChannelDistance = std::stod(value);
            else if (key == "ChannelWidth") settings.ChannelWidth = std::stod(value);
            else if (key == "MaximumDepth") settings.MaximumDepth = std::stod(value);
            else if (key == "SoundSpeed") settings.SoundSpeed = std::stoul(value);
            else if (key == "Angle") settings.Angle = std::stoul(value);
            else if (key == "GainStart") settings.GainStart = std::stoul(value);
            else if (key == "GainEnd") settings.GainEnd = std::stoul(value);
            else if (key == "Voltage") settings.Voltage = std::stoul(value);
            else if (key == "Iterations") settings.Iterations = std::stoul(value);
            else if (key == "NoiseLevel") settings.NoiseLevel = std::stoul(value);
            else if (key == "CyclesPerPulse") settings.CyclesPerPulse = std::stoul(value);
            else if (key == "TriggerMode") settings.TriggerMode = std::stoul(value);
            else if (key == "TriggerModeName") settings.TriggerModeName = value;
            else if (key == "ProfileLength") settings.ProfileLength = std::stoul(value);
            else if (key == "ProfilesPerBlock") settings.ProfilesPerBlock = std::stoul(value);
            else if (key == "Blocks") settings.Blocks = std::stoul(value);
            else if (key == "AmplitudeStored") settings.AmplitudeStored = (std::stoi(value) != 0);
            else if (key == "DoNotStoreDoppler") settings.DoNotStoreDoppler = (std::stoi(value) != 0);
            else if (key == "RawDataMin") settings.RawDataMin = std::stol(value);
            else if (key == "RawDataMax") settings.RawDataMax = std::stol(value);
            else if (key == "RawDataRange") settings.RawDataRange = std::stoul(value);
            else if (key == "AmplDataMin") settings.AmplDataMin = std::stol(value);
            else if (key == "AmplDataMax") settings.AmplDataMax = std::stol(value);
            else if (key == "VelocityInterpretingMode") settings.VelocityInterpretingMode = std::stol(value);
            else if (key == "UserSampleTime") settings.UserSampleTime = (std::stoi(value) != 0);
            else if (key == "SampleTime") settings.SampleTime = std::stoul(value);
            else if (key == "UseMultiplexer") settings.UseMultiplexer = (std::stoi(value) != 0);
            else if (key == "FlowMapping") settings.FlowMapping = (std::stoi(value) != 0);
            else if (key == "FirstValidChannel") settings.FirstValidChannel = std::stoul(value);
            else if (key == "LastValidChannel") settings.LastValidChannel = std::stoul(value);
            else if (key == "FlowRateType") settings.FlowRateType = std::stol(value);
            else if (key == "PeriodEnhOffset") settings.PeriodEnhOffset = std::stoul(value);
            else if (key == "PeriodEnhPeriod") settings.PeriodEnhPeriod = std::stoul(value);
            else if (key == "PeriodEnhNCycles") settings.PeriodEnhNCycles = std::stoul(value);
        }

        if (read_MUX_PARAMETER) {
            break;
        }
    }
    file.close();




}



