import numpy as np
from functools import reduce
import matplotlib.pyplot as plt
from scipy.special import jv


m_Max :int = 50 #定义求和的最大个数

cylinder_R :float = 72.5 #定义圆柱形容器的尺寸

freq_0 :float = 0.5 #定义容器转动频率

define_Visc = [500,1000,3000] #定义粘度的初值和猜测范围



def Deriv_AtPoint(
        y_nearpoint,#函数y数列
        x_nearpoint,#函数x数列
        ):
    #xy数列中元素个数应该为奇数，结果为
    #计算并输出函数某一点的导数，如果
    formula_1 = sum([(y_nearpoint[j]-np.mean(y_nearpoint))*(x_nearpoint[j]-np.mean(x_nearpoint)) for j in range(len(x_nearpoint))])
    formula_2 = sum([(x_nearpoint[j]-np.mean(x_nearpoint))**2 for j in range(len(x_nearpoint))])
    return formula_1/formula_2

def _PhaseDelay_Continuity(
        front_data,#前一个位置的数字
        target_data #现在要判断的数字
        ):
    #想方设法让计算出来的相位延迟连续，不会突然跳一个pi
    for times in range(10):
        if abs(front_data-target_data)>np.pi/4:
            target_data = target_data + np.pi if target_data<front_data else target_data - np.pi
        else:
            break
    return target_data

def Alpha_Bessel(
        cylinder_R, #定义圆柱形容器的尺寸
        freq_0,#定义容器转动频率
        visc,#定义粘度值
        position_array,#定义一个记录位置坐标的数组
        ):
    k = np.sqrt(np.pi*freq_0/visc)
    Beta = (-1+1j)*k
    Xi_R = Beta*cylinder_R
    Bessel_result_R = jv(1,Xi_R)
    Phi_R = np.real(Bessel_result_R)
    Psi_R = np.imag(Bessel_result_R)
    
    alpha_list = []
    for r in position_array:
        Xi_r = Beta*r
        Bessel_result_r = jv(1,Xi_r)
        Phi_r = np.real(Bessel_result_r)
        Psi_r = np.imag(Bessel_result_r)
        alpha = np.arctan(((Phi_r*Psi_R)-(Phi_R*Psi_r))/((Phi_r*Phi_R)+(Psi_r*Psi_R)))
        alpha_list.append(alpha if len(alpha_list) == 0 else _PhaseDelay_Continuity(alpha_list[-1],alpha))
    return np.array(alpha_list)

#自动化计算不同位置的粘度，采用二分法逼近的算法，计算量极高
prec = 1 #定义如果粘度预测范围的最大值和最小值的差小于此值的时候退出
result_visc = []
for i in range(3,len(position_r_array)-3):
#遍历可以求导的位置点
    rang_of_Visc = define_Visc.copy()
    experimental_value = ArgDelay_deriv[i-3]
    for WTF in range(50):
        #定义最大的迭代次数，如果迭代次数超过20，自动退出
        print('在'+str(i)+'点循环'+str(WTF+1)+'次，此时v_eff='+str(rang_of_Visc[1]))
        #采用二分法逼近最终值
        predicted_value = []
        for visc in rang_of_Visc:
            alpha_array = Alpha_Bessel(cylinder_R,freq_0,visc,position_r_array)
            for j in range(len(position_r_array)):
                alpha_array[j] = alpha_array[j] if alpha_array[j]*ArgDelay_array[j]>0 else -alpha_array[j]
            deriv_alpha = Deriv_AtPoint(alpha_array[i-3:i+4],position_r_array[i-3:i+4])#计算出这一点的alpha的导数
            predicted_value.append(deriv_alpha)
        if (predicted_value[0]-experimental_value)*(experimental_value-predicted_value[1])>0:#如果值在预定的粘度最小值和粘度当前值之前
            if abs(rang_of_Visc[0]-rang_of_Visc[2])<prec:
                #判断是否收敛
                print('在第'+str(i)+'点收敛\n============================================')
                break
            else:
               print('标准值:'+str(experimental_value))
               print('当前判断值:'+str(predicted_value))
               rang_of_Visc[2] = rang_of_Visc[1]
               rang_of_Visc[1] = (rang_of_Visc[0]+rang_of_Visc[1])/2
        elif (predicted_value[1]-experimental_value)*(experimental_value-predicted_value[2])>0:#如果值在预定的粘度当前值和粘度最大值值之前
            if abs(rang_of_Visc[0]-rang_of_Visc[2])<prec:
                #判断是否收敛
                print('在第'+str(i)+'点收敛\n============================================')
                break
            else:
               print('标准值:'+str(experimental_value))
               print('当前判断值:'+str(predicted_value))
               rang_of_Visc[0] = rang_of_Visc[1]
               rang_of_Visc[1] = (rang_of_Visc[1]+rang_of_Visc[2])/2
        else:
            print('在第'+str(i)+'点出错\n==============================================')
            print(predicted_value)
            print(experimental_value)
            print(rang_of_Visc)
            rang_of_Visc[1] = -1
            break
    result_visc.append(rang_of_Visc[1]) 
        

plt.figure()
plt.grid()
plt.xlim([500,1500])
plt.plot(result_visc,position_r_array[3:-3],'ro')
plt.show()

plt.figure()
plt.grid()
plt.ylim([500,1500])
plt.plot(ShearRate_array,result_visc,'ro')
plt.show()


#根据理论解测试输出相位延迟曲线
'''
alpha = Calculation_and_SortinOut_AlphaFunction(cylinder_R,0.5,1000,position_r_array)

plt.figure()
plt.xlabel(r'$ \alpha(r) [\pi] $')
plt.ylabel('r/R')
plt.grid ()
plt.plot(alpha,position_r_array/cylinder_r)
plt.show()
'''

'''
n = 2
x = range(200,2000,20)  
y = []
for vir in x:
    r_list = position_r_array[n:n+5]        
    alpha = np.array([_Calculation_Alpha_AtPoint(m_Max,cylinder_R,r,freq_0,vir,temp_phi_m,temp_psi_m) if _Calculation_Alpha_AtPoint(m_Max,cylinder_R,r,0.5,vir,temp_phi_m,temp_psi_m)*ArgDelay_array[n]>0 else-_Calculation_Alpha_AtPoint(m_Max,cylinder_R,r,0.5,vir,temp_phi_m,temp_psi_m) for r in r_list])       
    deriv_alpha = Deriv_AtPoint(alpha, r_list) 
    y.append(deriv_alpha)
plt.figure()
plt.grid()
#plt.ylim((-0.05,0.05))
plt.plot(x,y,'ro')
plt.show()   
'''

'''
alpha = np.array([calculation_alpha(m_Max,cylinder_R,r,0.5,200) for r in position_r_array])   
plt.figure()
plt.grid()
#plt.ylim((-0.05,0.05))
plt.plot(alpha,position_r_array)
plt.show()        
'''    
    



    