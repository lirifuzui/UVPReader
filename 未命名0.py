import numpy as np
import matplotlib.pyplot as plt
f_s = np.array([i/100 for i in range(101)])
y_r = np.array([i/20 for i in range(20,201)])
K = 1

f_s, y_r = np.meshgrid(f_s, y_r)

f_b = 1-f_s
D_ba = f_s*1+f_b*5
beta = 1+ 4/13*(8*0.637-1)*D_ba*(((5+D_ba)**2*(1-3/8*D_ba/(5+D_ba)))*f_b+
                              ((1+D_ba)**2*(1-3/8*D_ba/(1+D_ba)))*f_s)/((5**3-(5-D_ba)**3)*f_b + f_s)

phi_m = (125*f_b + f_s)/((5-D_ba)*f_b + (((5+D_ba)**3-(5-D_ba)**3)*f_b+(1+D_ba)**3*f_s)/beta)




phi =phi_m/(0.75/(np.sqrt(y_r*((2*y_r + 5*K)/(2+5*K))**(3/2))-1)+1)