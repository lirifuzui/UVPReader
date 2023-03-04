#引入容器尺寸 cylinder_r
#引入位置阵列 position_r_array
#引入计算精度Prec
import numpy as np
from math import atan

v = 1000
phi_r = []
psi_r = []
for  i in range(len(position_r_array)):
    Temp = []
    Temp2 = []
    for j in range(Prec):
        m = j+1
        Temp.append(Phi_r_array[i,j]*(v**(2*m+1)))
        Temp2.append(Psi_r_array[i,j]*(v**(2*m+1)))
    phi_r.append(sum(Temp))
    psi_r.append(sum(Temp2))
phi_r_array = np.array(phi_r)
psi_r_array = np.array(psi_r)

Temp = []
Temp2 = []   
for i in range(Prec):
    m = i+1
    Temp.append(Phi_R_array[i]*(v**(2*m+1)))
    Temp2.append(Psi_R_array[i]*(v**(2*m+1)))
phi_R = sum(Temp)
psi_R = sum(Temp2)


alpha_r = []
for i in range(len(position_r_array)):
    AA = phi_r_array[i]*psi_R - psi_r_array[i]*phi_R
    BB = phi_r_array[i]*phi_R + psi_r_array[i]*psi_R
    alpha_r.append(atan(AA/BB))


plt.figure()
plt.xlabel('$ \alpha(r) [\pi] $')
plt.ylabel('r/R')
plt.grid ()
plt.plot(alpha_r/np.pi,position_r_array/cylinder_r)
plt.show()