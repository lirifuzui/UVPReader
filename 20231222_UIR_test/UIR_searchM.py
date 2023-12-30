import matplotlib.pyplot as plt
import numpy as np

from pyuvp import ForMetflowUvp

files = ['sample_duty50-701hz.mfprof']

Visc = []
for file in files:
    data = ForMetflowUvp.readUvpFile(file)
    data.defineSoundSpeed(1029)
    vel_origin = data.velTables[0]
    coords_origin = data.coordinateArrays[0]
    analysis = data.createUSRAnalysis()
    analysis.channelRange(30, 110)
    analysis.pipeGeom(30, 25, 4.7, 1)

    analysis.slicing(1)

    analysis.rheologyViscocity_UIR(1.0,
                                min_viscosity=200, max_viscosity=1500, smooth_level=13,
                                ignoreException=True)

