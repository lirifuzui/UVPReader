import numpy as np
import matplotlib.pyplot as plt
K=1/300
y_r = np.array([i/20 for i in range(20,41)])

y = y_r*((2*y_r + 5*K)/(2+5*K))**(3/2)

phi_m = 0.637

plt.figure()

phi = 1/(2.5/np.log(y)+1/phi_m)
plt.plot(y_r, phi)
phi = (1-y**(-1/(2.5*phi_m)))*phi_m
plt.plot(y_r, phi)
phi = 1/(1.25/(y**(1/2)-1)+(1/phi_m))
plt.plot(y_r, phi)
phi = (1-y**(-1/2.5))*phi_m
plt.plot(y_r, phi)
phi = (1-y**(-1/2))*phi_m
plt.plot(y_r, phi)
phi = phi_m/(9/(8*y)+1)**3
plt.plot(y_r, phi)
phi = phi_m/(0.75/(y**(1/2)-1)+1)
plt.plot(y_r, phi)


phi_data = [0.1,0.15,0.2,0.25,0.3]
y_r_data = [378.95/300,396.7/300,441.79/300,512.21/300,591.42/300]
plt.scatter(y_r_data,phi_data)
plt.legend([
    "Mooney",
    "Krieger&Dougherty",
    "Eilers",
    "Roscoe",
    "Maron&Pierce",
    "Frankel&Acrivos",
    "Chong",
    "data"])
plt.show()