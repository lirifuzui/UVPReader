import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

plt.figure(figsize=(7, 6))
plt.rcParams['axes.linewidth'] = 2
plt.tick_params(axis='both', which='both', width=1.5, length=6)

files = ['5p/5p_d.csv', '10p/10p_d.csv', '15p/15p_d.csv', '25p/25p_d.csv', '30p/30p_d.csv']
for file in files:
    df = pd.read_csv(file, header=None)
    data = df.iloc[:, 0]

    kde = gaussian_kde(data)

    # 生成一组X值，用于绘制密度曲线
    D = np.linspace(0, max(data), 15)
    freq = kde(D)
    # 绘制密度分布函数图
    plt.step(D, freq, where='mid', label='Density')
    D_ba = np.mean(data)
    phi_m0 = 0.45
    part_1 = 0
    part_2 = 0
    part_3 = 0
    part_4 = 0
    part_5 = 0
    for n in range(12):
        part_1 += (D_ba + D[n]) ** 2 * (1 - 3 / 8 * D_ba / (D_ba + D[n])) * freq[n]
        part_2 += (D[n] ** 3 - ((D[n] - D_ba) if D[n] > D_ba else 0) ** 3) * freq[n]
        part_3 += D[n] ** 3 * freq[n]
        part_4 += ((D[n] - D_ba) if D[n] > D_ba else 0) ** 3 * freq[n]
        part_5 += ((D_ba + D[n]) ** 3 - ((D[n] - D_ba) if D[n] > D_ba else 0) ** 3) * freq[n]

    beta = 1 + 4 / 13 * (8 * phi_m0) * D_ba * part_1 / part_2

    phi_m = part_3 / (part_4 + part_5 / beta)
    print(phi_m)
plt.title('Density Distribution Plot')
plt.xlabel('X-axis')
plt.ylabel('Density')
plt.legend()
plt.show()
