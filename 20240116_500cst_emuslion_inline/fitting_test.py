import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from pyuvp import ForMetflowUvp
Volume_fraction = ["5p", "10p", "15p", "20p", "25p", "30p"]
# Duty = ["65", "70", "75"]
Duty = ["60", "65", "70", "75", "80"]
pressure_0 = [-216, -266, -273, -649.6, -652.8, -486.02]

i = 1
j = 3


volume_f = Volume_fraction[i]
duty = Duty[j]

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
data._data_show(1020)

vel = data.velTables[0] * 2
coords_origin = data.coordinateArrays[0] * np.cos(30 / 180 * np.pi)
coords_origin = coords_origin - 28.7
coords = coords_origin[11:165]
vel = np.mean(vel, axis=0)
vel = vel[11:165]
curve_coords = coords_origin[51:125]
curve_vel = vel[51:125]

plt.scatter(coords / 1000, vel / 1000)
plt.plot(coords / 1000, velosity_perfile(coords / 1000, 0.375))
plt.grid()
plt.show()