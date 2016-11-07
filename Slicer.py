# calls parser
# computes intersections
# determines inner support, external support, or empty space
# operates top down
# calculates extra for flat part

import Parser
import math
import GCode


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
        #print "z="+ str(z)
        #print(facetdata[z])
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
    if (len(points) == 1):
        #print "WTF"
        return [(points[0], points[0])]
    otherOutput = makePairs(points[2:])
    otherOutput.insert(0, (points[0], points[1]))
    return otherOutput

def getXLineSurfaceDiffs(coord, layerdata1, layerdata2, flip):
    #IGNORE TRIANGLES WOOOOOOOOT
    if (layerdata2 is None):
        #print "layerdata2 is None"
        return makePairs(intersections(coord, layerdata1, flip))
    above = intersections(coord, layerdata1, flip)
    below = intersections(coord, layerdata2, flip)
    #above.sort()
    #below.sort()
    #abovePairs = intersections(coord, layerdata1, flip)
    #belowPairs = intersections(coord, layerdata2, flip)
   # #print "above="+str(above)
   # #print "below="+str(below)
    totalPoints = above + below
    totalPoints.sort()
    total = intervalSetUnion(makePairs(totalPoints))
   # #print "total= "+ str(total)
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
            return [(base[0], subtracting[0])]
        if (subtracting[1] < base[1]) and (subtracting[0] <= base[0]):
            return [(subtracting[1], base[1])]
        return [(base[0], subtracting[0]), (subtracting[1], base[1])]
    return [base]

def intervalSetDiff(baseIntervals, subtracting):
    base = list(baseIntervals)
    for sub in subtracting:
        nextIterIntervals = []
        for b in base:
            diffResult = intervalDiff(b, sub)
          #  #print(base)
           # #print(str(b)+ " - " + str(sub)+" = "+str(diffResult))
            nextIterIntervals = nextIterIntervals + diffResult
        base = nextIterIntervals
    return base
def wrapIntersections(x, layerdata, flip):
    if (layerdata is None):
        return []
    results = intersections(x, layerdata, flip)
    results.sort()
    return makePairs (results)
    #return intersections(x, layerdata, flip)

def getSupportAndFillIntervals(x, xmin, xmax, layerData, layerdataBelow, layerdataAbove, accumulatedAbove, flip):
    #diff1 = getXLineSurfaceDiffs(x, layerData, layerdataBelow, flip)
    #diff2 = getXLineSurfaceDiffs(x, layerData, layerdataAbove, flip)
    maxInterval = [(xmin-1, xmax+1)]

    topInsides = wrapIntersections(x, layerdataAbove, flip)
    midInsides = wrapIntersections(x, layerData, flip)
    botInsides = wrapIntersections(x, layerdataBelow, flip)
    fill = intervalSetIntersect(intervalSetIntersect(topInsides, midInsides), botInsides)
    supportMaxArea = intervalSetDiff(maxInterval, accumulatedAbove)
    topSupport = intervalSetDiff(maxInterval, topInsides)
    midSupport = intervalSetDiff(maxInterval, midInsides)
    botSupport = intervalSetDiff(maxInterval, botInsides)
    support = intervalSetIntersect(intervalSetIntersect(intervalSetIntersect(topSupport, midSupport), botSupport), accumulatedAbove)
    #print("new fill = "+str(fill))
    #print("new support = " + str(support))
    surfaceLines = intervalSetUnion(intervalSetDiff(topInsides, fill) + intervalSetDiff(midInsides, fill) + intervalSetDiff(botInsides, fill))
    #print ("new surface = " + str (surfaceLines))
    #surfaceLines = intervalSetUnion(diff1 + diff2)
    ##print ("surfaceLines="+str(surfaceLines))
    ##print ("accAbove="+str(accumulatedAbove))
    #supportAndFill = intervalSetDiff(maxInterval, surfaceLines)
    ##print ("unsorted="+str(supportAndFill))
    #supportAndFill.sort(cmp=lambda first, second:cmp(first[0], second[0]))
    ##print "accAbove="+str(accumulatedAbove)
    ##print "suppAndFill="+str(supportAndFill)
    ##print "suppAndFill[0::2]="+str(supportAndFill[0::2])
    #support = intervalSetIntersect(accumulatedAbove, supportAndFill[0::2])
    #fill = intervalSetIntersect(accumulatedAbove, supportAndFill[1::2])
    return (surfaceLines, support, fill, intervalSetUnion(accumulatedAbove + surfaceLines))

def processLayer(z, facetdata, accDataX, accDataY, zdelta, xdelta, ydelta, supportSpacing, fillSpacing, xmin, xmax, ymin, ymax, zmin, zmax):
    layerData = facetdata[z]
    layerDataAbove = None
    layerDataBelow = None
    if (z*zdelta+zdelta <=zmax):
        layerDataAbove = facetdata[z+1]
    if (z*zdelta-zdelta >=zmin):
        layerDataBelow = facetdata[z-1]
    #print ("processing layer z=" + str(z))
    ##print "layerData = " + str(layerData)
    #print len(layerData)
    xFirstPass = {}
    yFirstPass = {}
    for x in range(int(math.floor(xmin/xdelta)),int(math.ceil(xmax/xdelta))+1):
        #print "x=" + str(x)
        (surfaceLines, support, fill, newAccData) = getSupportAndFillIntervals(x*xdelta, xmin, xmax, layerData, layerDataBelow, layerDataAbove, accDataX[x], False)
        #print "done x"
        accDataX[x] = newAccData
        xFirstPass[x] = (surfaceLines, support, fill)
    for y in range(int(math.floor(ymin/ydelta)),int(math.ceil(ymax/ydelta))+1):
        (surfaceLines, support, fill, newAccData) = getSupportAndFillIntervals(y*ydelta, ymin, ymax, layerData, layerDataBelow, layerDataAbove, accDataY[y], True)
        accDataY[y] = newAccData
        yFirstPass[y] = (surfaceLines, support, fill)
    return (xFirstPass, yFirstPass)


def processAll(xdelta, ydelta, zdelta, filename, supportSpacing, fillSpacing):
    (facetData, xmin, xmax, ymin, ymax, zmin, zmax) = generateSliceData(zdelta, filename)
    accIntervalsX = {}
    accIntervalsY = {}
    xFirstPass = {}
    yFirstPass = {}
    xOutput = {}
    gcode = GCode.GCodeWriter("foo.gcode", zdelta)
    for x in range(int(math.floor(xmin/xdelta)),int(math.ceil(xmax/xdelta))+1):
        accIntervalsX[x] = []
    for y in range(int(math.floor(ymin/ydelta)),int(math.ceil(ymax/ydelta))+1):
        accIntervalsY[y] = []
    #print (xmin, xmax, ymin, ymax, zmin, zmax)
    zrange = (range(int((math.floor(zmin/zdelta))), int(math.ceil(zmax/zdelta))+1))
    zrange.reverse()
    #print(zrange)
    for z in zrange:
        #print("z=" + str(z))
        (xFirstPassTemp, yFirstPassTemp) = processLayer(z, facetData, accIntervalsX, accIntervalsY, zdelta, xdelta, ydelta, supportSpacing, fillSpacing, xmin, xmax, ymin, ymax, zmin, zmax)
        xFirstPass[z] = xFirstPassTemp
        yFirstPass[z] = yFirstPassTemp
    #print "second pass"
    zrange.reverse()
    for z in zrange:
        #print ("z="+str(z))
        for line in facetData[z]:
            gcode.writeLayer(line[0], line[1])
        for x in range(int(math.floor(xmin/xdelta)),int(math.ceil(xmax/xdelta))+1):
            #print ("x="+str(x))
            above = ([], [], [])
            if (z*zdelta + zdelta <=zmax):
                above = xFirstPass[z+1][x]
            cur = xFirstPass[z][x]
            below = ([], [], [])
            if (z*zdelta -zdelta >= zmin):
                below = xFirstPass[z-1][x]
            newSurface = intervalSetUnion(above[0] + cur[0] + below[0])
            newFill = intervalSetDiff(cur[2], newSurface)
            newSupport = intervalSetDiff(cur[1], newSurface)
            xOutput = (newSurface, newSupport, newFill)
            #print ("surface = " + str(newSurface))
            #print ("fill = " + str(newFill))
            #print ("support = " + str(newSupport))
            #print (x)
            #print (fillSpacing)
            #print(x % fillSpacing)
            if ((x % fillSpacing) == 0):
                for fill in newFill:
                    gcode.writeLayer((x*xdelta,fill[0]), (x*xdelta,fill[1]))
                    #print(str(fill))
            if ((x % supportSpacing) == 0):
                for support in newSupport:
                    gcode.writeLayer((x*xdelta,support[0]), (x*zdelta,support[1]))
            for surf in newSurface:
                gcode.writeLayer((x*xdelta,surf[0]), (x*xdelta,surf[1]))
        gcode.incrementLayer()
        for line in facetData[z]:
            gcode.writeLayer(line[0], line[1])

    gcode.done()




processAll(0.1, 0.1, 0.1, "testData/sphere.stl", 10, 10)