import matplotlib.pyplot as plt

files = ["05hz45deg.mfprof","05hz60deg.mfprof","1hz40deg.mfprof","1hz30deg.mfprof"]

plt.figure()
plt.xlabel(r'Shear Rate $\gamma_{\mathrm{eff}}$ ')
plt.ylabel(r'Viscosity $\nu_{\mathrm{eff}}$')
plt.ylim(200, 400)
plt.xlim(3,15)
plt.grid()

for file in files:
    data = uvp.readFile(file)
    analysis = data.createUSRAnalysis()

    analysis.cylinderGeom(72.5, 38, 11.7)
    analysis.channelRange(156, 175)
    analysis.slicing(5)
    u_theta = analysis.velTableTheta()
    '''coordinates_r = analysis.coordSeries
    times = analysis.timeArrays()
    x = [choose_volume_f for choose_volume_f in range(len(coordinates_r))]
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

plt.show()
