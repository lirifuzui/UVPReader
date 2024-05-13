#ifndef READ_METFLOW_FILES_H
#define READ_METFLOW_FILES_H

#include <cstdint>

#include <fstream>
#include <sstream>
#include <iostream>

#include <string>
#include <vector>

#include <windows.h>

//定义保存测量参数的结构体
struct Settings {
    //header中的参数
    std::string signum;
    uint64_t measParamsOffset;
    uint32_t nProfiles;
    uint32_t reserved1;
    uint32_t flags;
    uint32_t recordSize;
    uint32_t nChannels;
    uint32_t reserved2;
    SYSTEMTIME  startTime;

    //[UVP_PARMAETER]
    uint32_t Frequency;
    double StartChannel;
    double ChannelDistance;
    double ChannelWidth;
    double MaximumDepth;
    uint32_t SoundSpeed;
    uint32_t Angle;
    uint32_t GainStart;
    uint32_t GainEnd;
    uint32_t Voltage;
    uint32_t Iterations;
    uint32_t NoiseLevel;
    uint32_t CyclesPerPulse;
    uint32_t TriggerMode;
    std::string TriggerModeName;
    uint32_t ProfileLength;
    uint32_t ProfilesPerBlock;
    uint32_t Blocks;
    bool AmplitudeStored;
    bool DoNotStoreDoppler;
    int RawDataMin;
    int RawDataMax;
    uint32_t RawDataRange;
    int AmplDataMin;
    int AmplDataMax;
    int VelocityInterpretingMode;
    bool UserSampleTime;
    uint32_t SampleTime;
    bool UseMultiplexer;
    bool FlowMapping;
    uint32_t FirstValidChannel;
    uint32_t LastValidChannel;
    int FlowRateType;
    uint32_t PeriodEnhOffset;
    uint32_t PeriodEnhPeriod;
    unsigned int PeriodEnhNCycles;
    std::string Comment;
    std::string MeasurementProtocol;

    //[MUX_PARAMETER]
    uint32_t NumberOfCycles;
    uint32_t CycleDelay;
    uint32_t Version;

    std::string allSettings;
};


//定义类
class ReadMetFlowFiles {
public:

    ReadMetFlowFiles(const std::string& file_path);

private:
    
    ULONGLONG FileTimeToMilliseconds(const FILETIME& ft); //用于获取FILETIME时间差的方法
    void readFile(); //读取文件，在实例化类的同时就被调用


public:
    Settings settings; //实例化参数设置的结构体

    std::vector<int32_t> profile_status;
    std::vector<int32_t> profile_transducers; //记录每个速度剖面的传感器编号
    std::vector<ULONGLONG> porfile_start_times; //每个速度剖面数据的记录时间，100纳秒位单位

private:
    //临时参数
    std::string file_path; // 保存文件路径
    FILETIME start_time; //保存读取的windows文件时间

    std::vector<std::vector<int16_t>> doppler_values; // 记录全部的多普勒数据
    std::vector<std::vector<int16_t>> amplitude_values; //记录全部的反射强度数据



};

#endif // READ_METFLOW_FILES_H
