#ifndef READ_METFLOW_FILES_H
#define READ_METFLOW_FILES_H

#include <cstdint>

#include <fstream>
#include <sstream>
#include <iostream>

#include <string>
#include <vector>

#include <windows.h>

struct Settings {
    std::string signum;
    uint64_t measParamsOffset;
    uint32_t nProfiles;
    uint32_t reserved1;
    uint32_t flags;
    uint32_t recordSize;
    uint32_t nChannels;
    uint32_t reserved2;
    SYSTEMTIME  startTime;


    std::string allSettings;
};

struct ProfileHeader {
    uint32_t status;
    uint32_t transducer;
    SYSTEMTIME profileTime;
};

class ReadMetFlowFiles {
public:
    ReadMetFlowFiles(const std::string& file_path);

private:
    void readFile();


public:
    Settings settings;

    ProfileHeader profile_header;

    std::vector<std::vector<int16_t>> doppler_values;
    std::vector<std::vector<int16_t>> amplitude_values;

    std::vector<int64_t> porfile_start_times; //每个速度剖面数据的记录时间，100纳秒位单位。

private:
    std::string file_path;
    FILETIME start_time;

};

#endif // READ_METFLOW_FILES_H
