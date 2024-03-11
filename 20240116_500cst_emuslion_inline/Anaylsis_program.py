import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from pyuvp import ForMetflowUvp

Volume_fraction = ["5p_", "10p_", "15p_", "20p_", "25p_"]
# Duty = ["65", "70", "75"]
Duty = ["60", "65", "70", "75", "80"]
pressure_0 = [681.51, 427.78, 427.17, 493.07, 665.88, -486.02]

for i, volume_f in enumerate(Volume_fraction):
    plt.figure()
    for duty in Duty:
        print(volume_f + duty)
        csv_file_path = volume_f + duty + 'duty.csv'
        df = pd.read_csv(csv_file_path)
        pressure = df.iloc[1:, 6].values
        pressure = (np.array(pressure) - pressure_0[i]) * 10
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
        coords_origin = coords_origin - 29.7
        coords = coords_origin[11:126]
        vel = np.mean(vel, axis=0)
        vel = vel[11:126]
        curve_coords = coords_origin[41:80]
        curve_vel = vel[41:80]
        params, covariance = curve_fit(velosity_perfile, curve_coords / 1000, curve_vel / 1000, p0 = 0.5)

        plt.scatter(coords / 1000, vel / 1000)
        plt.plot(coords / 1000, velosity_perfile(coords / 1000, params[0]))
        print("visco:" + str(params[0]))

    ''' try:
            print(volume_f + duty)
            csv_file_path = volume_f + duty + 'duty.csv'
            df = pd.read_csv(csv_file_path)
            pressure = df.iloc[1:, 6].values
            pressure = (np.array(pressure) - pressure_0[i]) * 10
            Rudio = 0.025
            L = 0.46
            delta_P = np.mean(pressure)
            print("delta_P:" + str(delta_P))



            def velosity_perfile(r, miu):
                return delta_P / (4 * miu * L) * (Rudio ** 2 - (r) ** 2)


            data = ForMetflowUvp.readFile(volume_f + "-" + duty + "duty.mfprof")
            data.defineSoundSpeed(1020)

            vel = data.velTables[0] * 2
            coords_origin = data.coordinateArrays[0] * np.cos(30 / 180 * np.pi)
            coords_origin = coords_origin - 28.7
            coords = coords_origin[11:165]
            vel = np.mean(vel, axis=0)
            vel = vel[11:165]
            curve_coords = coords_origin[51:125]
            curve_vel = vel[51:125]
            params, covariance = curve_fit(velosity_perfile, curve_coords / 1000, curve_vel / 1000, p0=0.5)

            plt.scatter(coords / 1000, vel / 1000)
            plt.plot(coords / 1000, velosity_perfile(coords / 1000, params[0]))
            print("visco:" + str(params[0]))
        except:
            continue'''
    print('===============================')
    plt.grid()
    plt.show()
