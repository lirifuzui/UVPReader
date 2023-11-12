import matplotlib.pyplot as plt
import numpy as np

K = 1 / 600
y_r = np.array([i / 20 for i in range(20, 51)])

y = y_r*((2*y_r + 5*K)/(2+5*K))**(3/2)

phi_m = 0.51

plt.figure()

phi = 1 / (1.25 / (y ** (1 / 2) - 1) + (1 / phi_m))
plt.plot(y_r, phi, label='Eilers')
phi = (1 - y ** (-1 / 2.5 / phi_m)) * phi_m
plt.plot(y_r, phi, label='Krieger and Dougherty')
phi = phi_m / (9 / (8 * y) + 1) ** 3
plt.plot(y_r, phi, label='Frankel and Acrivos')
phi = phi_m / (0.75 / (y ** (1 / 2) - 1) + 1)
plt.plot(y_r, phi, label='Chong')

# phi_data = [0.1, 0.15, 0.2, 0.25, 0.3]
# y_r_data = [376 / 300, 417 / 300, 441 / 300, 498 / 300, 559 / 300]

phi_data = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
y_r_data = [709 / 600, 764 / 600, 822 / 600, 920 / 600, 1050 / 600, 1220 / 600]
y_r_upper = [41 / 600, 65 / 600, 109 / 600, 94 / 600, 84 / 600, 69 / 600]
y_r_under = [59 / 600, 85 / 600, 26 / 600, 53 / 600, 53 / 600, 66 / 600]
plt.errorbar(y_r_data, phi_data, color="black", xerr=[y_r_under, y_r_upper], fmt='o', capsize=4)

plt.scatter(y_r_data, phi_data, color="black")
# plt.legend()
plt.show()
