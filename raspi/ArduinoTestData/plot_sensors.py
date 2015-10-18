import sys
import matplotlib.pyplot as plt

fname = sys.argv[1]

sensordata = []

with open(fname, 'r') as f:
    sensordata = [[int(x.replace('\n', '')) for x in line[2:].split(',')] for line in f.readlines() if line[:2] == '0|']

def plot(label, vals):
    plt.plot(range(len(vals)), vals)
    plt.ylabel(label)
    plt.draw()

def movingaverage(interval, window_size):
    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window)

from scipy import signal

#maxVal = 32768.0
#normalizedVals = [ v * 1.0 / maxVal for v in y]

normalizedVals = [v[-2] * 1.0 / 32768 for v in sensordata]

plot('normed', normalizedVals)
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


# Filter requirements.
order = 3
fs = 5.0       # sample rate, Hz
#cutoff = 3.667  # desired cutoff frequency of the filter, Hz
cutoff = 1 
#min_value_threshold = 0.2

avgVal = reduce(lambda x,y: x + y, normalizedVals) * 1.0 / len(normalizedVals)
lowPassed = butter_lowpass_filter(normalizedVals, cutoff, fs, order)
print 'lowpassed', lowPassed
plot('lp', lowPassed)
plt.show()

peaks = signal.argrelmax(lowPassed)
print 'peaks', peaks
peakVals = [lowPassed[x] for x in peaks[0]]
accepted_peaks = [lowPassed[x] for x in peaks[0] if lowPassed[x] > 0.05]
print 'initial peaks', peakVals
print 'accepted peaks', accepted_peaks
print 'average', avgVal
print len(accepted_peaks)

