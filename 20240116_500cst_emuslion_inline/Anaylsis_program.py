import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from pyuvp import ForMetflowUvp

Volume_fraction = ["5p", "10p", "15p", "20p", "25p", "30p"]
# Duty = ["65", "70", "75"]
Duty = ["60", "65", "70", "75", "80", "85"]
pressure_0 = [681.51, 427.78, 427.17, 493.07, 665.88, 667.27]

for i, volume_f in enumerate(Volume_fraction):
    plt.figure()
    for duty in Duty:
        print(volume_f + duty)
        csv_file_path = volume_f +'_' + duty + 'duty.csv'
        df = pd.read_csv(csv_file_path)
        pressure = df.iloc[1:, 6].values
        pressure = (np.array(pressure) - pressure_0[i]) * 10
        Rudio = 0.025
        L = 0.46
        delta_P = np.mean(pressure)
        print("delta_P:" + str(delta_P))


        def velosity_perfile(r, miu):
            return delta_P / (4 * miu * L) * (Rudio ** 2 - (r) ** 2)


        data = ForMetflowUvp.readUvpFile(volume_f + "_" + duty + "duty.mfprof")
        data.defineSoundSpeed(1020)

        vel = data.velTables[0] * 2
        coords_origin = data.coordinateArrays[0] * np.cos(30 / 180 * np.pi)
        coords_origin = coords_origin - 30
        coords = coords_origin[11:128]
        vel = np.mean(vel, axis=0)
        vel = vel[11:128]
        curve_coords = coords_origin[51:95]
        curve_vel = vel[51:95]
        params, covariance = curve_fit(velosity_perfile, curve_coords / 1000, curve_vel / 1000, p0=0.5)
        plt.scatter(coords / 1000, vel / 1000)
        plt.plot(coords / 1000, velosity_perfile(coords / 1000, params[0]))
        print("visco:" + str(params[0]))
    print('===============================')
    plt.grid()
    plt.show()
