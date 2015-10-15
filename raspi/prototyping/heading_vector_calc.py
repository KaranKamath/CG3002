from scipy import sin, cos
from math import radians

average_dist = 10 * 50 * 1.0 / 4

headings = [0, 270, 0, 90] # right, down, right, up

vectorsX = [average_dist * cos(radians(heading))
            for heading in headings]
vectorsY = [average_dist * sin(radians(heading))
            for heading in headings]

print average_dist
print sum(vectorsX), sum(vectorsY)

average_dist = 10 * 50 * 1.0 / 4

headings = [270, 0, 270, 180] # down, right, down, left

vectorsX = [average_dist * cos(radians(heading))
            for heading in headings]
vectorsY = [average_dist * sin(radians(heading))
            for heading in headings]

print '\n'
print average_dist
print int(sum(vectorsX).round()), int(sum(vectorsY).round())
