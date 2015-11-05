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
#threshold = 6100.0
#print '\n', threshold

import matplotlib.pyplot as plt

def plot(label, vals):
    plt.plot(range(len(vals)), vals)
    plt.ylabel(label)
    plt.draw()

y = avgVals
x = range(len(avgVals))

def movingaverage(interval, window_size):
    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window)

y = avgVals
from scipy import signal

maxVal = 32768.0
normalizedVals = [ v * 1.0 / maxVal for v in y]

plot('normed', y)
plt.show()


def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = signal.lfilter(b, a, data)
    return y


## Filter requirements.
#order = 5
#fs = 10.0       # sample rate, Hz
##cutoff = 3.667  # desired cutoff frequency of the filter, Hz
#cutoff = 1.5 
#min_value_threshold = 0.2
#
#avgVal = reduce(lambda x,y: x + y, normalizedVals) * 1.0 / len(normalizedVals)
#lowPassed = butter_lowpass_filter(normalizedVals, cutoff, fs, order)
#print 'lowpassed', lowPassed
#plot('lp', lowPassed)
#plt.show()
#
#peaks = signal.argrelmax(lowPassed)
#print 'peaks', peaks
#peakVals = [lowPassed[x] for x in peaks[0]]
#accepted_peaks = [lowPassed[x] for x in peaks[0] if lowPassed[x] > min_value_threshold]
#print 'initial peaks', peakVals
#print 'accepted peaks', accepted_peaks
#print 'average', avgVal
#print len(accepted_peaks)


from pykalman import KalmanFilter
kf = KalmanFilter(n_dim_state=1, n_dim_obs=1)
#print y
#output=kf.em(y).smooth(normalizedVals)[0]
##print output
#plot('kalman', output)
#plt.show()


#means, covariances = kf.filter(y[0])
import numpy as np
means = np.zeros((1,1))
covariances = np.zeros((1,1))

output = []

next_mean, next_covariance = kf.filter_update(
        means[-1], covariances[-1], y[0]
    )

for new_measurement in y[1:]:
    next_mean, next_covariance = kf.filter_update(
        next_mean, next_covariance, new_measurement
    )

    print next_mean, next_covariance
    output.append(next_mean[0])

print output
plot('Filtered', output)
plt.show()
