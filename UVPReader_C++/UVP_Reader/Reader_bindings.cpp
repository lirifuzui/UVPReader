#include <pybind11/pybind11.h>
#include "ReadMetFlowFiles.h"

namespace py = pybind11;

PYBIND11_MODULE(readuvpfiles, m) {
    py::class_<Settings>(m, "Settings")
        .def(py::init<>())
        .def_readwrite("signum", &Settings::signum)
        .def_readwrite("measParamsOffset", &Settings::measParamsOffset)
        .def_readwrite("nProfiles", &Settings::nProfiles)
        .def_readwrite("reserved1", &Settings::reserved1)
        .def_readwrite("flags", &Settings::flags)
        .def_readwrite("recordSize", &Settings::recordSize)
        .def_readwrite("nChannels", &Settings::nChannels)
        .def_readwrite("reserved2", &Settings::reserved2)
        .def_readwrite("startTime", &Settings::startTime)
        .def_readwrite("allSettings", &Settings::allSettings);

    py::class_<ReadMetFlowFiles>(m, "ReadMetFlowFiles")
        .def(py::init<const std::string&>())
        .def_readonly("settings", &ReadMetFlowFiles::settings);
}
