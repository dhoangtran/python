import numpy
import math

def generateDistances(nRows, nCols, unit, distances_file):
    
    f = open(distances_file, 'w')

    nRegions = nRows * nCols
    distances = numpy.zeros((nRegions, nRegions))
    for r1 in range(nRegions):
        for r2 in range(nRegions):
            x1 = r1 / nCols
            y1 = r1 % nCols
            x2 = r2 / nCols
            y2 = r2 % nCols
            distances[r1, r2] = math.sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2)) * unit
            
            f.write(str(distances[r1,r2]))
            f.write(' ')
        f.write('\n')
    
    f.close()
    #return distances
    
nRows = 4
nCols = 4
unit = 1.0
distances_file = 'C:/Users/r0660215/Dropbox/Research/Taxi dispatching/Datasets/stdp/distances.txt'
generateDistances(nRows, nCols, unit, distances_file)
