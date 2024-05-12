cmake_minimum_required(VERSION 3.4...3.18)
project(readuvpfiles)

add_subdirectory(pybind11)
pybind11_add_module(readuvpfiles Reader_bindings.cpp ReadMetFlowFiles.cpp)