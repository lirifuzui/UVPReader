from pyuvp import uvp

data = uvp.readData("1000min.mfprof")
# vel = data.velTables[0]
# anaylsis = data.createUSRAnalysis()
# anaylsis.cylinderGeom(77, 66, 15)
# anaylsis.channelRange(77, 110)
# anaylsis.slicing(0)
# viscoity, shearrate = anaylsis.rheologyViscosity()
# anaylsis.rheologyViscoelasticity(1000)
'''
plt.scatter(shearrate, viscoity, s=3, alpha=0.5)
plt.grid()
plt.ylim(500, 1500)
plt.show()'''
