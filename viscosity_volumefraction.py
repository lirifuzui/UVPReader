import matplotlib.pyplot as plt
import numpy as np

K = 1 / 600
y_r = np.array([i / 20 for i in range(20, 51)])

y = y_r*((2*y_r + 5*K)/(2+5*K))**(3/2)

phi_m = 0.57

plt.figure(figsize=(7, 6))
plt.rcParams['axes.linewidth'] = 2
plt.tick_params(axis='both', which='both', width=1.5, length=6)

phi = 1 / (1.25 / (y ** (1 / 2) - 1) + (1 / phi_m))
plt.plot(phi, y_r, label='Eilers')
phi = (1 - y ** (-1 / 2.5 / phi_m)) * phi_m
plt.plot(phi, y_r, label='Krieger and Dougherty')
#phi = phi_m / (9 / (8 * y) + 1) ** 3
#plt.plot(phi, y_r, label='Frankel and Acrivos',color = "green")
phi = phi_m / (0.75 / (y ** (1 / 2) - 1) + 1)
plt.plot(phi, y_r, label='Chong')

'''phi_data = [0.1, 0.15, 0.2, 0.25, 0.3]
y_r_data = [376 / 300, 417 / 300, 441 / 300, 498 / 300, 559 / 300]'''

phi_data = [0.05, 0.1, 0.15, 0.25, 0.3]
y_r_data = [776 / 650, 827 / 650, 929 / 650, 1171 / 650, 1419 / 650]
y_r_upper = [40 / 650, 53 / 650, 76 / 650, 31 / 650, 52 / 650]
y_r_under = [21 / 650, 34 / 650, 36 / 650, 47 / 650, 43 / 650]
plt.errorbar(phi_data, y_r_data, color="black", yerr=[y_r_under, y_r_upper], fmt='o', capsize=4)

plt.scatter(phi_data, y_r_data, color="black")
plt.legend()
plt.show()
