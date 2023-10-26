import numpy as np

files = [55, 60, 65, 70, 75, 80]

for n, file in enumerate(files):
    # 定义拟合函数
    diff_P = 1000
    Rudio = 0.025 / 2
    L = 0.46


    def velosity_perfile(r, miu):
        return diff_P / (4 * miu * L) * (Rudio ** 2 - (r / 1000) ** 2)


    # 文件数据
    data = uvp.readUvpFile(str(file) + ".mfprof")
    data.defineSoundSpeed(1010)
    vel = data.velTables[0] * 2
    coords_origin = data.coordinateArrays[0] * np.cos(30 / 180 * np.pi)
    coords = []
    for i in range(len(coords_origin)):
        coords.append(np.abs(coords_origin[i] - (10.26 + 25)))

    coords = np.array(coords[21:33])
    vel = vel[:, 21:33]
    vel = np.mean(vel, axis=0)
    du_dr = np.abs(np.gradient(vel, coords))
    alpha = float(press_diff[n] / 0.46)
    visc = alpha * coords / (2 * du_dr)

