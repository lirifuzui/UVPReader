import numpy as np
import matplotlib.pyplot as plt
f_s = np.array([i/100 for i in range(101)])
y_r = np.array([i/20 for i in range(20,201)])
K = 0.5
f_s, y_r = np.meshgrid(f_s, y_r)

f_b = 1-f_s
D_ba = f_s*1+f_b*5
beta = 1+ 4/13*(8*0.637-1)*D_ba*(((5+D_ba)**2*(1-3/8*D_ba/(5+D_ba)))*f_b+
                              ((1+D_ba)**2*(1-3/8*D_ba/(1+D_ba)))*f_s)/((5**3-(5-D_ba)**3)*f_b + f_s)

phi_m = (125*f_b + f_s)/((5-D_ba)**3*f_b + (((5+D_ba)**3-(5-D_ba)**3)*f_b+(1+D_ba)**3*f_s)/beta)

y = y_r*((2*y_r + 5*K)/(2+5*K))**(3/2)
phi =(1-y**(-1/2.5))*phi_m

fig, ax = plt.subplots()
ax.spines['top'].set_linewidth(2)
ax.spines['right'].set_linewidth(2)
ax.spines['bottom'].set_linewidth(2)
ax.spines['left'].set_linewidth(2)
ax.tick_params(axis='both', which='both', width=2)
plt.yscale('log')
# plt.grid()
plt.ylabel("Relative viscosity")
plt.xlabel("Vol. fraction of fine particle")
plt.contour(f_s, y_r, phi, levels=np.arange(0, 1.1, 0.1), cmap='jet')
plt.colorbar()
plt.title('K='+str(K))
plt.show()


#==================================================================
plt.figure()
for k in K:
    y_r = np.array([i/50 for i in range(52,126)])
    phi_e =0.637/(0.75/(np.sqrt(y_r*((2*y_r + 5*k)/(2+5*k))**(3/2))-1)+1)
    de_phi = np.gradient(phi_e,y_r)
    plt.plot(phi_e, y_r*0.05*de_phi/phi_e, label=k)
    #plt.plot(y_r, phi_e)
last_181_rows = phi[:,:181]
max_values = np.zeros(181)
min_values = np.zeros(181)
for i in range(181):
    max_values = np.max(last_181_rows,axis = 1)
    min_values = np.min(last_181_rows,axis = 1)
# plt.fill_between(y_r, max_values, min_values, alpha=0.3, color = "red")
'''plt.ylabel("predicted error(volume fraction)")
plt.xlabel("volume fraction")
plt.legend()
plt.grid()
plt.show()  '''
