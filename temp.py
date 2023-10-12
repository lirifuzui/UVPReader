import matplotlib.pyplot as plt
import numpy as np

K = 1 / 300
y_r = np.array([i / 20 for i in range(20, 91)])

y = y_r*((2*y_r + 5*K)/(2+5*K))**(3/2)

phi_m = 0.58

plt.figure()

phi = 1 / (1.25 / (y ** (1 / 2) - 1) + (1 / phi_m))
plt.plot(y_r, phi, label='Eilers')
phi = (1 - y ** (-1 / 2.5 / phi_m)) * phi_m
plt.plot(y_r, phi, label='Krieger and Dougherty')
phi = phi_m / (9 / (8 * y) + 1) ** 3
plt.plot(y_r, phi, label='Frankel and Acrivos')
phi = phi_m / (0.75 / (y ** (1 / 2) - 1) + 1)
plt.plot(y_r, phi, label='Chong')

phi_data = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
y_r_data = [776 / 757, 798 / 734, 927 / 734, 1104 / 734, 1272 / 734, 1457 / 734]
plt.scatter(y_r_data, phi_data)
plt.legend()
plt.show()
