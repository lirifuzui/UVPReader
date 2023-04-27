from pyuvp import uvp, usr
import matplotlib.pyplot as plt
import numpy as np


files = ["1hz30deg.mfprof","1hz45deg.mfprof","1hz60deg.mfprof","05hz60deg.mfprof","05hz90deg.mfprof","05hz120deg.mfprof","05hz150deg.mfprof"]
# files = ["05hz60deg.mfprof","05hz90deg.mfprof","05hz120deg.mfprof","05hz150deg.mfprof"]
plt.figure()
plt.xlabel(r'Shear Rate $\gamma_{\mathrm{eff}}$ ')
plt.ylabel(r'Viscosity $\nu_{\mathrm{eff}}$')
plt.ylim(500, 2000)

for file in files:
    data = uvp.readData(file)
    data.resetSoundSpeed(1029)
    vel_origin = data.velTables[0]

    analysis = data.createUSRAnalysis()
    analysis.cylinderGeom(72.5, 71.54, 11.35)
    analysis.coordsClean(55, 85)
    analysis.timeSlicing(10)
    u_theta = analysis.velTableTheta()
    coordinates_r = analysis.coordSeries
    times = analysis.timeSeries()
    '''x = [i for i in range(len(coordinates_r))]
    vibration_frequency, max_magnitude, phase_delay, phase_delay_derivative, real_part, imag_part = analysis.doFFT()
    plt.plot(phase_delay_derivative, coordinates_r)
    plt.grid()
    plt.show()'''

    '''u = np.transpose(u_theta[0:50, :])
    time = times[0:50]
    plt.figure()
    plt.ylabel('R')
    plt.xlabel('t [s]')
    #plt.ylim(0.65, 1)
    plt.contourf(time, coordinates_r, u, cmap="bwr", levels=20)
    plt.colorbar()
    plt.show()'''

    visc, shearrate = analysis.calculate_Viscosity_ShearRate(smooth_level= 9,ignoreException=True)
    visc_t = visc.reshape((11,30))
    shearrate_t = shearrate.reshape((11,30))
    visc = np.sum(visc_t,axis=0)/11
    shearrate = np.sum(shearrate_t,axis=0)/11

    plt.scatter(shearrate, visc, label=file)


plt.grid()
plt.legend()
plt.show()
