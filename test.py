import os
from datetime import datetime

path = "C:/Users/ZHENG WENQING/Desktop/UVPReader/乳液粘度模型"
root_path = os.path.abspath(os.path.join(path, os.pardir))
current_time = datetime.now()
output_folder_name = current_time.strftime("%Y%m%d%H%M%S")
os.mkdir(path + "/" + "aaa")
