import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from pyuvp import ForMetflowUvp

Volume_fraction = ["5p"]
# Duty = ["65", "70", "75"]
Duty = ["60", "65", "70", "75", "80"]
pressure_0 = [[422.9580273, 130.1262049, 133.1574688, 131.7361953, 424.8387448]]

for i, volume_f in enumerate(Volume_fraction):
    plt.figure()
    for j, duty in enumerate(Duty):
        print(volume_f + duty)
        csv_file_path = volume_f + duty + 'duty.csv'
        df = pd.read_csv(csv_file_path)
        pressure = df.iloc[1:, 6].values
        pressure = (np.array(pressure) - pressure_0[i][j]) * 10
        Rudio = 0.025
        L = 0.46
        delta_P = np.mean(pressure)
        print("delta_P:" + str(delta_P))


        def velosity_perfile(r, miu):
            return delta_P / (4 * miu * L) * (Rudio ** 2 - (r) ** 2)


        data = ForMetflowUvp.readFile(volume_f + duty + "duty.mfprof")
        data.defineSoundSpeed(1020)

        vel = data.velTables[0] * 2
        coords_origin = data.coordinateArrays[0] * np.cos(30 / 180 * np.pi)
        coords_origin = coords_origin - 30
        coords = coords_origin[11:165]
        vel = np.mean(vel, axis=0)
        vel = vel[11:165]
        curve_coords = coords_origin[41:135]
        curve_vel = vel[41:135]
        params, covariance = curve_fit(velosity_perfile, curve_coords / 1000, curve_vel / 1000, p0=0.5)

        plt.scatter(coords / 1000, vel / 1000)
        plt.plot(coords / 1000, velosity_perfile(coords / 1000, params[0]))
        print("visco:" + str(params[0]))
    print('===============================')
    plt.grid()
    plt.show()
