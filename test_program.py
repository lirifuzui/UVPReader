import matplotlib.pyplot as plt

from pyuvp import uvp

data = uvp.readData("1000min.mfprof")
vel = data.velTables[0]
anaylsis = data.createUSRAnalysis()
anaylsis.cylinderGeom(77, 66, 15)
anaylsis.channelRange(77, 110)
anaylsis.slicing(5, 500)
aa = anaylsis.timeSeries(1)
bb = anaylsis.velTableTheta(1)

# viscoity, shearrate = anaylsis.rheologyViscosity()
a, b, c, d = anaylsis.rheologyViscoelasticity(1000, 2000)
plt.scatter(a, c)
plt.grid()
plt.show()

'''
plt.scatter(shearrate, viscoity, s=3, alpha=0.5)
plt.grid()
plt.ylim(500, 1500)
plt.show()'''
