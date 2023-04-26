from pyuvp import usr,uvp
import numpy as np
import matplotlib.pyplot as plt

data = uvp.readData("1000min.mfprof")
vel = data.velTables[0]
anaylsis = data.createUSRAnalysis()
anaylsis.cylinderGeom(77,66,15)
anaylsis.coordsClean(77, 110)
viscoity,shearrate = anaylsis.calculate_Viscosity_ShearRate()

plt.scatter(shearrate, viscoity)
plt.grid()
plt.ylim(500, 1500)
plt.show()
