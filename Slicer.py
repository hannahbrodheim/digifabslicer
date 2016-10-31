# calls parser
# computes intersections
# determines inner support, external support, or empty space
# operates top down
# calculates extra for flat part

import Parser
import math


def generateSliceData(zdelta, filename):
    (facets, xmin, xmax, ymin, ymax, zmin, zmax) = Parser.parse(filename, zdelta)

    facetdata = {}
    for z in range(int(math.floor(zmin/zdelta)), int(math.ceil(zmax/zdelta))+1):
       # triangles = []
        lines = []
        for facet in facets:
        #    if facet.isExactlyFlat(zdelta):
        #        triangles.add(facet)
       #     else:
            intersection = facet.getIntersectionLine(z*zdelta)
            if intersection is not None:
                lines.append(intersection)
        facetdata[z] = lines
        print "z="+ str(z)
        print(facetdata[z])
    return (facetdata, xmin, xmax, ymin, ymax, zmin, zmax)

def intersections(coord, layerdata, flip):
    points = []
    for line in layerdata:
        first = line[0]
        second = line[1]
        x1 = first[0]
        y1 = first[1]
        x2 = second[0]
        y2 = second[1]
        if flip:
            t = x1
            x1 = y1
            y1 = t
            t = x2
            x2 = y2
            y2 = t
        if (x1<= coord and coord <= x2):
            if x1==x2:
                continue
            points.append((((coord-x1)*y1) + ((x2-coord)*y2))/(x2-x1))
        elif (x2<=coord and coord<=x1):
            if x2==x1:
                continue
            points.append((((coord-x2)*y2) + ((x1-coord)*y1))/(x1-x2))
    return points

def makePairs(points):
    if points==[]:
        return []
    otherOutput = makePairs(points[2:])
    otherOutput.insert(0, (points[0], points[1]))
    return otherOutput

def getXLineSurfaceDiffs(coord, layerdata1, layerdata2, flip):
    #IGNORE TRIANGLES WOOOOOOOOT
    if (layerdata2 is None):
        print "layerdata2 is None"
        return makePairs(intersections(coord, layerdata1, flip))
    above = intersections(coord, layerdata1, flip)
    below = intersections(coord, layerdata2, flip)
    print "above="+str(above)
    print "below="+str(below)
    totalPoints = above + below
    totalPoints.sort()
    total = intervalSetUnion(makePairs(totalPoints))
    print "total= "+ str(total)
    return total

def intervalIntersect(interval1, interval2):
    return (max(interval1[0], interval2[0]), min(interval1[1], interval2[1]))

def intervalUnion(interval1, interval2):
    return (min(interval1[0], interval2[0]), max(interval1[1], interval2[1]))

def intervalHasOverlap(interval1, interval2):
    return (interval1[0] >= interval2[0] and interval1[0] <= interval2[1]) or (interval1[1] >= interval2[0] and interval1[1] <= interval2[1]) or (interval2[0] >=interval1[0] and interval2[1] <= interval1[1]) or (interval1[0] >= interval2[0] and interval1[1] <= interval2[1])

def intervalSetUnion(intervals):
    queue = intervals
    output = []
    while (not queue == []):
        interval = queue[0]
        queue = queue[1:]
        found = False
        for out in output:
            if intervalHasOverlap(interval, out):
                output.remove(out)
                queue.append(intervalUnion(out, interval))
                found = True
                break
        if (not found):
            output.append(interval)
    return output

#pairwise intersection
def intervalSetIntersect(intervals1, intervals2):
    temp = []
    for int1 in intervals1:
        for int2 in intervals2:
            if intervalHasOverlap(int1, int2):
                temp.append(intervalIntersect(int1, int2))

    return intervalSetUnion(temp)

def intervalDiff(base, subtracting):
    if intervalHasOverlap(base, subtracting):
        if (subtracting[1] >= base[1]) and (subtracting[0] <= base[0]):
            return []
        if (subtracting[1] >= base[1]) and (subtracting[0] > base[0]):
            print "foo"
            return [(base[0], subtracting[0])]
        if (subtracting[1] < base[1]) and (subtracting[0] <= base[0]):
            print "bar"
            return [(subtracting[1], base[1])]
        return [(base[0], subtracting[0]), (subtracting[1], base[1])]
    return [base]

def intervalSetDiff(baseIntervals, subtracting):
    base = list(baseIntervals)
    for sub in subtracting:
        nextIterIntervals = []
        for b in base:
            diffResult = intervalDiff(b, sub)
            print(base)
            print(str(b)+ " - " + str(sub)+" = "+str(diffResult))
            nextIterIntervals = nextIterIntervals + diffResult
        base = nextIterIntervals
    return base

def getSupportAndFillIntervals(x, xmin, xmax, layerData, layerdataBelow, layerdataAbove, accumulatedAbove, flip):
    diff1 = getXLineSurfaceDiffs(x, layerData, layerdataBelow, flip)
    diff2 = getXLineSurfaceDiffs(x, layerData, layerdataAbove, flip)
    surfaceLines = intervalSetUnion(diff1 + diff2)
    print ("surfaceLines="+str(surfaceLines))
    print ("accAbove="+str(accumulatedAbove))
    maxInterval = [(xmin-1, xmax+1)]
    supportAndFill = intervalSetDiff(maxInterval, surfaceLines)
    print ("unsorted="+str(supportAndFill))
    supportAndFill.sort(cmp=lambda first, second:cmp(first[0], second[0]))
    print "accAbove="+str(accumulatedAbove)
    print "suppAndFill="+str(supportAndFill)
    print "suppAndFill[0::2]="+str(supportAndFill[0::2])
    support = intervalSetIntersect(accumulatedAbove, supportAndFill[0::2])
    fill = supportAndFill[1::2]
    return (surfaceLines, support, fill, intervalSetUnion(accumulatedAbove + surfaceLines))

def processLayer(z, facetdata, accDataX, accDataY, zdelta, xdelta, ydelta, supportSpacing, fillSpacing, xmin, xmax, ymin, ymax, zmin, zmax):
    layerData = facetdata[z]
    layerDataAbove = None
    layerDataBelow = None
    if (z*zdelta+zdelta <=zmax):
        layerDataAbove = facetdata[z+1]
    if (z*zdelta-zdelta >=zmin):
        layerDataBelow = facetdata[z-1]
    print ("processing layer z=" + str(z))
    print "layerData = " + str(layerData)
    print len(layerData)
    for x in range(int(math.floor(xmin/xdelta)),int(math.ceil(xmax/xdelta))+1):
        print "x=" + str(x)
        (surfaceLines, support, fill, newAccData) = getSupportAndFillIntervals(x*xdelta, xmin, xmax, layerData, layerDataBelow, layerDataAbove, accDataX[x], False)
        #TODO output gcode
        print "done x"
        accDataX[x] = newAccData
        print ("x=" + str(x) + " surfaceLines=" + str(surfaceLines) + " support = " + str(support) + " fill = " + str(fill))

    #for y in range(int(math.floor(ymin/ydelta)),int(math.ceil(ymax/ydelta))+1):
    #    y = y * ydelta
    #    (surfaceLines, support, fill, newAccData) = getSupportAndFillIntervals(y, layerData, layerDataBelow, layerDataAbove, accDataY[y], True)
    #    #TODO output gcode
    #    accDataY[y] = newAccData
    return (accDataX, accDataY)

def processAll(xdelta, ydelta, zdelta, filename, supportSpacing, fillSpacing):
    (facetData, xmin, xmax, ymin, ymax, zmin, zmax) = generateSliceData(zdelta, filename)
    accIntervalsX = {}
    accIntervalsY = {}
    for x in range(int(math.floor(xmin/xdelta)),int(math.ceil(xmax/xdelta))+1):
        accIntervalsX[x] = []
    for y in range(int(math.floor(ymin/ydelta)),int(math.ceil(ymax/ydelta))+1):
        accIntervalsY[y] = []
    print (xmin, xmax, ymin, ymax, zmin, zmax)
    zrange = (range(int((math.floor(zmin/zdelta))), int(math.ceil(zmax/zdelta))+1))
    zrange.reverse()
    print(zrange)
    for z in zrange:
        print("z=" + str(z))
        (accIntervalsX2, accIntervalsY2) = processLayer(z, facetData, accIntervalsX, accIntervalsY, zdelta, xdelta, ydelta, supportSpacing, fillSpacing, xmin, xmax, ymin, ymax, zmin, zmax)
        accIntervalsX = accIntervalsX2
        accIntervalsY = accIntervalsY2

processAll(0.1, 0.1, 0.1, "testData/testcube_20mm.stl", 2, 2)