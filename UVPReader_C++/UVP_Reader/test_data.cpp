#include "ReadMetFlowFiles.h"
#include <iostream>
#include <thread>
#include <chrono>
#include <numbers>

//常量测试
/*
int main() {
    double pi = std::numbers::pi;
    return 0;
}
*/



//时间戳测试
/*
ULONGLONG FileTimeToMilliseconds(const FILETIME& ft) {
    ULARGE_INTEGER ull;
    ull.LowPart = ft.dwLowDateTime;
    ull.HighPart = ft.dwHighDateTime;
    return ull.QuadPart / 10000; // 100 nanoseconds to milliseconds
}
FILETIME GetCurrentTimestamp() {
    FILETIME currentTimestamp;
    GetSystemTimeAsFileTime(&currentTimestamp);
    return currentTimestamp;
}
int main() {
    FILETIME currentTimestamp = GetCurrentTimestamp();
    std::this_thread::sleep_for(std::chrono::seconds(5));
    FILETIME fivesceondTimestamp = GetCurrentTimestamp();
    ULONGLONG diffMilliseconds;
    diffMilliseconds = FileTimeToMilliseconds(fivesceondTimestamp) - FileTimeToMilliseconds(currentTimestamp);

    // 输出时间差
    std::cout << "时间差为：" << diffMilliseconds << " 毫秒" << std::endl;
    return 0;
}
*/


int main() {
    // 创建readFile对象并指定文件名
    try {
        ReadMetFlowFiles reader("C:/Users/ZHENG WENQING/Desktop/UVPReader/examples/example_1.mfprof");

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

        std::cout << "\nTimeline:" << reader.porfilesStartTime[0] << std::endl;
        std::cout << "Timeline:" << reader.porfilesStartTime[1] << std::endl;
        std::cout << "Timeline:" << reader.porfilesStartTime[2] << std::endl;
        std::cout << "Timeline:" << reader.porfilesStartTime[3] << std::endl;
        std::cout << "Timeline:" << reader.porfilesStartTime[4] << std::endl;
        std::cout << "Timeline:" << reader.porfilesStartTime[5] << std::endl;
        std::cout << "Timeline:" << reader.porfilesStartTime[6] << std::endl;
        std::cout << "Timeline:" << reader.porfilesStartTime[7] << std::endl;

        std::cout << "\nTransducers:" << reader.profilesTransducerNumber[0] << std::endl;
        std::cout << "Transducers:" << reader.profilesTransducerNumber[1] << std::endl;
        std::cout << "Transducers:" << reader.profilesTransducerNumber[2] << std::endl;
        std::cout << "Transducers:" << reader.profilesTransducerNumber[3] << std::endl;
        std::cout << "Transducers:" << reader.profilesTransducerNumber[4] << std::endl;
        std::cout << "Transducers:" << reader.profilesTransducerNumber[5] << std::endl;
        std::cout << "Transducers:" << reader.profilesTransducerNumber[6] << std::endl;

        std::cout << "\nFrequency:" << reader.settings.Frequency << std::endl;
        std::cout << "SoundSpeed:" << reader.settings.SoundSpeed << std::endl;
        std::cout << "StartChannel:" << reader.settings.StartChannel << std::endl;
        std::cout << "RawDataMin:" << reader.settings.RawDataMin << std::endl;
        std::cout << "FlowMapping: " << (reader.settings.FlowMapping ? "true" : "false") << std::endl;
        std::cout << "PeriodEnhNCycles:" << reader.settings.PeriodEnhNCycles << std::endl;


    }catch (const std::runtime_error& e) {
        std::cerr << e.what() << std::endl;
        // Handle the error, e.g., log it, notify the user, etc.
    }
   
    return 0;
}
