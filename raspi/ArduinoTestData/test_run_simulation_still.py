import sys

filename = sys.argv[1]

xAccVals = []
yAccVals = []
zAccVals = []

#factor = 0.000061
factor = 1.0
with open(filename) as f:
    filedata = f.readlines()
    xAccVals = [factor * int(line.split()[1].replace(',', ''))  for line in filedata if line[:2] == '1|']
    yAccVals = [factor * int(line.split()[2].replace(',', ''))  for line in filedata if line[:2] == '1|']
    zAccVals = [factor * int(line.split()[3].replace(',', ''))  for line in filedata if line[:2] == '1|']

with open('HoursOfData.txt') as f:
    filedata = f.readlines()
    xStillAccVals = [factor * int(line.split(',')[0].replace('1|', ''))  for line in filedata if line[:2] == '1|']
    yStillAccVals = [factor * int(line.split(',')[1]) for line in filedata if line[:2] == '1|']
    zStillAccVals = [factor * int(line.split(',')[2]) for line in filedata if line[:2] == '1|']

import numpy as np

from itertools import imap

avgVals = list(imap(lambda x, y, z: 1.0 * (x + y + z) / 3.0, xAccVals, yAccVals, zAccVals))
avgStillVals = list(imap(lambda x, y, z: 1.0 * (x + y + z) / 3.0, xStillAccVals, yStillAccVals, zStillAccVals))
#threshold = sum(avgStillVals[10:-10]) * 1.0 / (len(avgStillVals) - 20)
threshold = 6100.0
print '\n', threshold

import matplotlib.pyplot as plt

def plot(label, vals):
    stillVals = [threshold] * len(vals)
    plt.plot(range(len(vals)), vals)
    plt.plot(range(len(stillVals)), stillVals)
    plt.ylabel(label)
    plt.show()

x = avgVals
y = range(len(avgVals))

def movingaverage(interval, window_size):
    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window)

x_av = movingaverage(x, 3)
plot('movingavg', x_av)
