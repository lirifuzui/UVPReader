import os
import multiprocessing

# 获取主机的核心数
num_cores = multiprocessing.cpu_count()
print("Number of CPU cores:", num_cores)

