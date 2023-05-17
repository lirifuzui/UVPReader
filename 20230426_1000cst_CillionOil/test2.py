import matplotlib.pyplot as plt

from pyuvp import uvp

files = ["05hz60deg.mfprof","05hz75deg.mfprof","1hz45deg.mfprof","1hz30deg.mfprof"]

plt.figure()
plt.xlabel(r'Shear Rate $\gamma_{\mathrm{eff}}$ ')
plt.ylabel(r'Viscosity $\nu_{\mathrm{eff}}$')
plt.ylim(0, 2000)

for file in files:
    data = uvp.readData(file)
    vel_origin = data.velTables[0]

    analysis = data.createUSRAnalysis()
    analysis.cylinderGeom(72.5, 46.69, 11.6)
    analysis.channelRange(165, 215)
    analysis.slicing(0)
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

    visc, shearrate = analysis.viscosity(ignoreException=True)
    plt.scatter(shearrate, visc)

plt.grid()

plt.show()
