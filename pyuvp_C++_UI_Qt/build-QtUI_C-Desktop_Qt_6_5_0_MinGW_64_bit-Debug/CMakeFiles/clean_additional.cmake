# Additional clean files
cmake_minimum_required(VERSION 3.16)

if("${CONFIG}" STREQUAL "" OR "${CONFIG}" STREQUAL "Debug")
  file(REMOVE_RECURSE
  "CMakeFiles\\QtUI_C_autogen.dir\\AutogenUsed.txt"
  "CMakeFiles\\QtUI_C_autogen.dir\\ParseCache.txt"
  "QtUI_C_autogen"
  )
endif()
