import numpy as np
from scipy.signal import argrelextrema

x = np.array([2,1,3,4,5,1,4,1,3,4,2])

# for local maxima
print argrelextrema(x, np.greater)

