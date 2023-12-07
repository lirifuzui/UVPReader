import matplotlib.pyplot as plt
import numpy as np

K = 1 / 600
y_rs = np.linspace(1, 3, 30)
phi_ms = np.linspace(0.45, 0.7, 30)

phi1 = np.zeros((30,30))
phi2 = np.zeros((30,30))
phi3 = np.zeros((30,30))
phi4 = np.zeros((30,30))

for j, y_r in enumerate(y_rs):
    for i, phi_m in enumerate(phi_ms):
        y = y_r * ((2 * y_r + 5 * K) / (2 + 5 * K)) ** (3 / 2)
        phi1[i,j] = 1 / (1.25 / (y ** (1 / 2) - 1) + (1 / phi_m))
        phi2[i,j] = (1 - y ** (-1 / 2.5 / phi_m)) * phi_m
        phi3[i,j] = phi_m / (9 / (8 * y) + 1) ** 3
        phi4[i,j] = phi_m / (0.75 / (y ** (1 / 2) - 1) + 1)



X, Y = np.meshgrid(y_rs, phi_ms)
plt.contourf(X, Y, phi2)
plt.colorbar()
plt.xlabel('y')
plt.ylabel('phi_m')
plt.show()
'''plt.plot(phi, y_r, label='Eilers')
plt.plot(phi, y_r, label='Krieger and Dougherty')
plt.plot(phi, y_r, label='Frankel and Acrivos',color = "green")
plt.plot(phi, y_r, label='Chong')'''