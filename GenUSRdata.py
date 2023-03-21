import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator

plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['mathtext.fontset'] = 'cm'
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
import numpy as np
from scipy.special import jv

# Declarations -----------------------------------------------------------------
# -- Parameter setting ---------------------------------------------------------
RR = 72.5  # [mm] Radius of vessel
Dy = 20  # [mm] Displacement of TDX
DX0 = 50  # [mm] Distance of TDx from cylinder wall
Dt = 0.05  # [sec] Time resolution
Dxi = 1.5  # [mm] Spatial resolution of UVP
ws = 1.7  # [mm] Starting position of measurement window

f0 = 1.0  # [Hz] OScillation frequency of the cylinder
Ang = 90  # [deg] Oscillation amplitude in degree

Nosc = 20.0  # number of oscillation periods

nuset = 1000  # [mm^2/s] Kinematic viscosity of test fluid

nlev = 0.03  # Noise level relative to the wall velocity

# -- Calculated parameters -----------------------------------------------------
omega0 = 2.0 * np.pi * f0  # [rad/s] Angular frequency of oscillation
Uwall = (Ang * np.pi / 180.0) * omega0 * RR  # [mm/s] Wall velocity

Nxi = int(np.trunc((DX0 - ws + np.sqrt(RR ** 2 - Dy ** 2)) / Dxi))  # Numer of spatial file_data point
Nt = int(np.trunc(Nosc / f0 / Dt))

# -- Output --------------------------------------------------------------------
fname = "u_xi500cSt1Hz90deg_vel"
ofile1 = fname + ".png"
ofile2 = fname + ".csv"

# -- Matrices formation --------------------------------------------------------
ur = np.zeros((Nt, Nxi))  # [mm/s] Radia velocity distribution

xi = np.arange(ws, ws + Nxi * Dxi, step=Dxi)  # Measurement point
ri = np.sqrt((DX0 + np.sqrt(RR ** 2 - Dy ** 2) - xi) ** 2 + Dy ** 2)  # Radial position
ti = np.arange(0.0, Nt * Dt, step=Dt)  # Time

# Velocity profile calculation from Bessel function ----------------------------

beta = (-1 + 1j) * np.sqrt(omega0 / 2.0 / nuset) * RR  # [-] Thickness of viscous layer
br = ri / RR * beta / 2.0  # beta r/2
bRR = 1.0 * beta / 2.0  # beta R/2

# -- Bessel function
J1r = jv(1, br)  # J_1(r, nu); r = rn
J1RR = jv(1, bRR)  # J_1(r, nu); r = R at the wall

Phir = J1r.real;
PhiRR = J1RR.real  # Extraction of real part
Psir = J1r.imag;
PsiRR = J1RR.imag  # Extractin of imaginary part

Usin = Phir * PhiRR + Psir * PsiRR
Ucos = PhiRR * Psir - Phir * PsiRR

for ii in range(Nxi):
    if xi[ii] > DX0:  # Remaining zero file_data out of cylinder
        ur[:, ii] = Usin[ii] * np.sin(omega0 * ti) + Ucos[ii] * np.cos(omega0 * ti)

noise = nlev * Uwall * np.random.randn(Nt, Nxi)  # Created random noise
ur = ur * Uwall / (PhiRR ** 2 + PsiRR ** 2) + noise

# alphar = np.arctan((Psir * PhiRR - Phir * PsiRR) / (Phir * PhiRR + Psir * PsiRR))

# file_data output in csv frmat------------------------------------------------------

uxi = ur * Dy / ri.reshape(Nxi, 1).T  # from u_r to u_xi
data = np.insert(uxi, 0, ti, axis=1)  # inserting time stamp
pos = np.insert(xi, 0, np.NaN)
data = np.insert(data, 0, pos, axis=0)  # inserting xi information

header = ',1,,,\n nProfiles,nChannels,MinSampTimeValue[msec],ChannelDistance[mm],VelResolution[mm/s],start[mm],nu[mm^2/s],f0[Hz],Theta[deg],R[mm],xi_Wall[mm]\n' \
         + str(Nt) + ',' + str(Nxi) + ',' + str(Dt * 1000) + ',' + str(Dxi) + ',-,' + str(ws) + ',' + str(
    nuset) + ',' + str(f0) + ',' + str(Ang) + ',' + str(RR) + ',' + str(DX0) + ','

np.savetxt(ofile2, data, fmt='%7.4f', delimiter=',', comments='', header=header)

# Graphics ---------------------------------------------------------------------

xj, tj = np.meshgrid(xi, ti)

levels = MaxNLocator(nbins=64, integer=True).tick_values(-np.max(uxi), np.max(uxi))

cmap = plt.get_cmap('seismic')
norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)

fig, ax1 = plt.subplots(figsize=(9, 3.4))

# contours are *point* based plots, so convert our bound into point
# cente
cf = ax1.contourf(tj + Dt / 2.,
                  xj + Dxi / 2., uxi, levels=levels,
                  cmap=cmap)
fig.colorbar(cf, ax=ax1, ticks=[-np.max(uxi), -np.max(uxi) / 2, 0, np.max(uxi) / 2, np.max(uxi)])

plt.xticks(np.arange(0, Nosc * 1.01 / f0, step=2.0 / f0))
ax1.set_xticks(np.arange(0, Nosc * 1.01 / f0, step=0.5 / f0), minor=True)
plt.yticks(np.arange(0, ws + Nxi * Dxi * 1.01, step=50))
ax1.set_yticks(np.arange(0, ws + Nxi * Dxi * 1.01, step=10), minor=True)
plt.xlabel(r"$t$ [s]", fontsize=14)
plt.ylabel(r"$\xi$ [mm]", fontsize=14)
plt.text(1.15, 0.5, r"$u_{\xi}$ [mm/s]", horizontalalignment="center",
         verticalalignment="center", rotation='vertical',
         transform=ax1.transAxes, fontsize=14)

plt.text(0.5, 1.1,
         r'$\nu$ = ' + str(nuset) + r' [mm$^2$/s], $f_0 = $' + str(f0) + r' [Hz], $\Theta$ = ' + str(Ang) + r' [deg]',
         horizontalalignment="center",
         verticalalignment="center", transform=ax1.transAxes, fontsize=14)

# adjust spacing between subplots so `ax1` title and `ax0` tick labels
# don't overlap
fig.tight_layout()

plt.savefig(ofile1, dpi=300)
plt.show()

# Program termination-----------------------------------------------------------
