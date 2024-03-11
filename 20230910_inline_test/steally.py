import numpy as np

emulsion_name = 'emulsion30'

files = ["_duty60", "_duty65", "_duty70", "_duty75", "_duty80"]

for file in files:
    data = uvp.readFile(emulsion_name + file + ".mfprof")
    # data.redefineSoundSpeed(1029)
    vel_origin = data.velTables[0]
    coords_origin = data.coordinateArrays[0] * np.cos(30 / 180 * np.pi)
    vel_ave = np.mean(vel_origin, axis=0)
    csv_file = emulsion_name + file + '.csv'
    combined_array = np.column_stack((coords_origin, vel_ave))



