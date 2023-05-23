import os

path = "C:/Users/ZHENG WENQING/Desktop/UVPReader/乳液粘度模型/1.861167.pdf"
a = open("aaa")
root_path = os.path.abspath(os.path.join(path, os.pardir))
print(root_path)
