import numpy as np
import matplotlib.pyplot as plt
'''D_ba = 16.1445283
phi_m0 = 0.523
D = np.array([2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5, 57.5, 62.5, 67.5, 72.5, 77.5, 82.5])
freq = np.array([13, 33, 42, 29, 16, 10, 10, 3, 0, 1, 0, 1, 0, 0, 0, 0, 0]) / 158'''



#生成一个高斯分布数列
# 设定均值和标准差
means = np.linspace(10, 70, 30)
std_devs = np.linspace(10, 70, 30)
phi_m_result = np.zeros((30, 30))
for i, mean in enumerate(means):
    for j, std_dev in enumerate(std_devs):

        # 生成x值范围
        x = np.linspace(1, 150, 100)

        # 计算对应x值的高斯分布的y值
        y = (1 / (std_dev * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean) / std_dev) ** 2)

        '''# 绘制高斯分布曲线
        plt.plot(x, y, label='Gaussian Distribution')

        # 添加标题和标签
        plt.title('Gaussian Distribution')
        plt.xlabel('x')
        plt.ylabel('Probability Density')

        # 添加图例
        plt.legend()

        # 显示图形
        plt.show()'''

        phi_m0 = 0.523
        part_1 = 0
        part_2 = 0
        part_3 = 0
        part_4 = 0
        part_5 = 0
        for n in range(17):
            part_1 += (mean + x[n]) ** 2 * (1 - 3 / 8 * mean / (mean + x[n])) * y[n]
            part_2 += (x[n] ** 3 - ((x[n] - mean) if x[n] > mean else 0) ** 3) * y[n]
            part_3 += x[n] ** 3 * y[n]
            part_4 += ((x[n] - mean) if x[n] > mean else 0) ** 3 * y[n]
            part_5 += ((mean + x[n]) ** 3 - ((x[n] - mean) if x[n] > mean else 0) ** 3) * y[n]

        beta = 1 + 4 / 13 * (8 * phi_m0) * mean * part_1 / part_2

        phi_m_result[i,j] = part_3 / (part_4 + part_5 / beta)

X, Y = np.meshgrid(std_devs, means)
plt.contourf(X, Y, phi_m_result)
plt.xlabel('std_dev')
plt.ylabel('mean')
plt.show()

