#include "ReadMetFlowFiles.h"
#include <iostream>

int main() {
    // 创建readFile对象并指定文件名
    ReadMetFlowFiles reader("C:/Users/ZHENG WENQING/Desktop/UVPReader/examples/example_2.mfprof");


    std::cout << "Signum:" << reader.settings.signum << std::endl;
    std::cout << "measParamsOffset:" << reader.settings.measParamsOffset << std::endl;
    std::cout << "nProfiles:" << reader.settings.nProfiles << std::endl;
    std::cout << "reserved1:" << reader.settings.reserved1 << std::endl;
    std::cout << "flags:" << reader.settings.flags << std::endl;
    std::cout << "recordSize:" << reader.settings.recordSize << std::endl;
    std::cout << "nChannels:" << reader.settings.nChannels << std::endl;
    std::cout << "reserved2:" << reader.settings.reserved2 << std::endl;
    std::cout << "fileTimeYear:" << reader.settings.startTime.wYear << std::endl;
    std::cout << "fileTimeMonth:" << reader.settings.startTime.wMonth << std::endl;
    std::cout << "fileTimeDay:" << reader.settings.startTime.wDay << std::endl;
    std::cout << "fileTimeHour:" << reader.settings.startTime.wHour << std::endl;
    std::cout << "fileTimeMinute:" << reader.settings.startTime.wMinute << std::endl;
    std::cout << "fileTimeSecond:" << reader.settings.startTime.wSecond << std::endl;
    std::cout << "fileTimeMillisecond:" << reader.settings.startTime.wMilliseconds << std::endl;
    

    std::cout << "\nstartTimeHour:" << reader.profile_header.profileTime.wHour << std::endl;
    std::cout << "startTimeMinute:" << reader.profile_header.profileTime.wMinute << std::endl;
    std::cout << "startTimeSecond:" << reader.profile_header.profileTime.wSecond << std::endl;
    std::cout << "startTimeMillisecond:" << reader.profile_header.profileTime.wMilliseconds << std::endl;
    
    std::cout << "\ntransducer:" << reader.profile_header.transducer << std::endl;

    std::cout << "\nstatus:" << reader.profile_header.status << std::endl;

    return 0;
}
