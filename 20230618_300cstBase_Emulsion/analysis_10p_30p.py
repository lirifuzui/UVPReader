import matplotlib.pyplot as plt
import numpy as np

# files = ["10p_05hz90deg.mfprof", "10p_05hz120deg_2.mfprof", "10p_05hz150deg.mfprof", "10p_1hz60deg.mfprof", "10p_1hz90deg.mfprof", "10p_1hz120deg.mfprof"]
# files = ["15p_05hz90deg.mfprof","15p_05hz120deg.mfprof","15p_05hz150deg.mfprof","15p_1hz60deg_2.mfprof", "15p_1hz90deg_2.mfprof", "15p_1hz120deg.mfprof"]
# files = ["20p_1hz90deg.mfprof","20p_1hz120deg.mfprof","20p_1hz60deg.mfprof","20p_05hz120deg.mfprof","20p_05hz90deg.mfprof","20p_05hz150deg.mfprof",]
# files = ["25p_1hz90deg.mfprof","25p_1hz120deg.mfprof","25p_1hz60deg.mfprof","25p_05hz120deg.mfprof","25p_05hz90deg.mfprof","25p_05hz150deg.mfprof",]
files = ["30p_1hz120deg_2.mfprof","30p_1hz60deg.mfprof","30p_1hz90deg.mfprof","30p_05hz90deg.mfprof","30p_05hz150deg.mfprof","30p_05hz120deg.mfprof",]
csv_filename = "30pdata.csv"

plt.figure(figsize=(7, 6))
# 设置坐标轴刻度线条粗度
plt.rcParams['axes.linewidth'] = 3
plt.tick_params(axis='both', which='both', width=1.5, length=6)
plt.xlabel(r'Shear Rate $\gamma_{\mathrm{eff}}$ ')
plt.ylabel(r'Viscosity $\nu_{\mathrm{eff}}$')
plt.ylim(0, 800)
Visc = []
Shear_rate = []
Coord = []
for file in files:
    data = uvp.readUvpFile(file)
    # data.redefineSoundSpeed(1029)
    vel_origin = data.velTables[0]
    coords_origin = data.coordinateArrays[0]
    analysis = data.createUSRAnalysis()
    analysis.channelRange(90, 100)
    analysis.cylinderGeom(77, 106.77, 10.62)

    analysis.slicing(20)

    shearrate, visc = analysis.rheologyViscosity(smooth_level=9, ignoreException=True)
    # plt.scatter(shearrate, visc, s=5, alpha=0.3, label=file, color = "black")
    Visc.extend(list(visc))
    for n in range(21):
        Coord.extend(list(analysis.coordSeries))
    Shear_rate.extend(list(shearrate))

# 初始化存储平均值、最大值和最小值的数组
arr_visc = []

# 循环每次循环
for i in range(21*6):
    # 计算每次循环对应位置的平均值、最大值和最小值
    start_idx = i * 10
    end_idx = (i + 1) * 10
    subset = Visc[start_idx:end_idx]
    arr_visc.append(subset)

arr_visc = np.array(arr_visc)
avg_visc = np.mean(arr_visc,axis=0)
min_visc = np.min(arr_visc,axis=0)
max_visc = np.max(arr_visc,axis=0)
Coord = Coord[0:10]

plt.plot(Coord, avg_visc, label='平均值', color='b', marker='o')
plt.fill_between(Coord, min_visc, max_visc, alpha=0.2, color='b', label='误差区域')

# 添加标签和标题
plt.xlabel('距离')
plt.ylabel('结果')
plt.title('距离-结果平均值曲线')

# 添加图例
plt.legend()

# 显示图形
plt.show()