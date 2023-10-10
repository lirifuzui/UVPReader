import numpy as np

D_ba = 16.1445283
phi_m0 = 0.523
D = np.array([2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5, 57.5, 62.5, 67.5, 72.5, 77.5, 82.5])
freq = np.array([13, 33, 42, 29, 16, 10, 10, 3, 0, 1, 0, 1, 0, 0, 0, 0, 0]) / 158
part_1 = 0
part_2 = 0
part_3 = 0
part_4 = 0
part_5 = 0
for n in range(17):
    part_1 += (D_ba + D[n]) ** 2 * (1 - 3 / 8 * D_ba / (D_ba + D[n])) * freq[n]
    part_2 += (D[n] ** 3 - ((D[n] - D_ba) if D[n] > D_ba else 0) ** 3) * freq[n]
    part_3 += D[n] ** 3 * freq[n]
    part_4 += ((D[n] - D_ba) if D[n] > D_ba else 0) ** 3 * freq[n]
    part_5 += ((D_ba + D[n]) ** 3 - ((D[n] - D_ba) if D[n] > D_ba else 0) ** 3) * freq[n]

beta = 1 + 4 / 13 * (8 * phi_m0) * D_ba * part_1 / part_2

phi_m = part_3 / (part_4 + part_5 / beta)
print(phi_m)
