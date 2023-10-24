import matplotlib.pyplot as plt
import time
from pyuvp import uvp
start = time.time()
data = uvp.readUvpFile("1000min.mfprof", num_threads=10, is_output=False)
data.defineSoundSpeed(1000)
vel = data.velTables[0]
times = data.timeArrays[0]
coords = data.coordinateArrays[0]

plt.figure()
plt.contour(coords, times, vel)
#plt.show()

anaylsis = data.createUSRAnalysis(num_threads = 1)
anaylsis.cylinderGeom(77, 66, 15)
anaylsis.channelRange(77, 100)
anaylsis.slicing(40)

viscoity, shearrate = anaylsis.rheologyViscosity()
'''a, b, c, d = anaylsis.rheologyViscoelasticity(1000, 2000)
plt.scatter(a, c)
plt.grid()
plt.show()'''


plt.scatter(viscoity, shearrate, s=3, alpha=0.5)
plt.grid()
plt.ylim(500, 1500)
#plt.show()
end = time.time()
print('程序执行时间: ', end - start)

