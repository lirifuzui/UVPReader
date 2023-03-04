# 从NS方程计算相位延迟需要准确的粘度数据
#因此我们先把不需要粘度参与计算的通解计算出来，减少后面的计算时间
from functools import reduce
import numpy as np

#定义精度,越大越好，但是太大计算时间会变长
Prec :int = 10
#引入容器尺寸 cylinder_r
cylinder_r = 72.5
#引入位置阵列 position_r_array

#计算Phi_m和Psi_m
Phi_m = []
Psi_m = []
for i in range(Prec):
    m :int = i+1
    m_factorial :int = reduce(lambda x,y:x*y,range(1,m+1)) #计算m！
    m_1_factorial :int = reduce(lambda x,y:x*y,range(1,m+2)) #计算(m+1)！
    An = (2**m)/(m_factorial*m_1_factorial)
    fm = (-1)**((m+2)/2) if (m&1)==0 else (-1)**((m+1)/2) #计算fm
    gm = (-1)**(m/2) if (m&1)==0 else (-1)**((m+1)/2) #计算gm
    temp = An*fm
    Phi_m.append(temp)
    temp = An*gm
    Psi_m.append(temp)
       
Phi_m_array = np.array(Phi_m)
Psi_m_array = np.array(Psi_m)

Phi_R = []
Psi_R = []
for i in range(Prec):
    m :int = i+1
    Phi_R.append(Phi_m_array[i]*(cylinder_r/2)**(2*m+1))
    Psi_R.append(Psi_m_array[i]*(cylinder_r/2)**(2*m+1))

Phi_R_array = np.array(Phi_R)
Psi_R_array = np.array(Psi_R)    

Phi_r = []
Psi_r = []

for r in position_r_array:
    Temp = []
    Temp2 = []
    for i in range(Prec):
        m :int = i+1
        Temp.append((Phi_m_array[i]*(r/2)**(2*m+1)))
        Temp2.append((Psi_m_array[i]*(r/2)**(2*m+1)))
    Phi_r.append(Temp)
    Psi_r.append(Temp)
    
Phi_r_array = np.array(Phi_r)
Psi_r_array = np.array(Psi_r)  


        
        




    


    
    







    
    
    
    
    
    
