import cppyy

# 加载 C++ 模块
cppyy.include("hello.cpp")

# 调用 C++ 函数
cppyy.gbl.printHello()