#include "ReadMetFlowFiles.h"


ReadMetFlowFiles::ReadMetFlowFiles(const std::string& file_path) : file_path(file_path) {
    readFile();
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

    for (size_t  i = 0; i < settings.nProfiles; ++i) {
        //读取Profile Header，临时存储在结构体变量profile_header中。
        file.read(buffer, sizeof(uint32_t));
        profile_header.status = *reinterpret_cast<uint32_t*>(buffer);

        file.read(buffer, sizeof(uint32_t));
        profile_header.transducer = *reinterpret_cast<uint32_t*>(buffer);

        file.read(buffer, sizeof(FILETIME));
        start_time = *reinterpret_cast<FILETIME*>(buffer);
        FileTimeToSystemTime(&start_time, &profile_header.profileTime);

        // 清空通道数据
        doppler_values_in_channels.clear();
        amplitude_values_in_channels.clear();

        //开始循环读取Dopplerdata和Amplitudedata
        for (size_t i = 0; i < settings.nChannels; ++i) {
            if (include_Doppler) {
                file.read(reinterpret_cast<char*>(&doppler_value), sizeof(int16_t));
                doppler_values_in_channels.push_back(doppler_value);
            }
            if (include_Doppler) {
                file.read(reinterpret_cast<char*>(&amplitude_value), sizeof(int16_t));
                amplitude_values_in_channels.push_back(amplitude_value);
            }
        }
        if (include_Doppler) {
            doppler_values.push_back(doppler_values_in_channels);
        }
        if (include_Doppler) {
            amplitude_values.push_back(amplitude_values_in_channels);
        }
    }
    file.close();

}

