# calls parser
# computes intersections
# determines inner support, external support, or empty space
# operates top down
# calculates extra for flat part

import Parser


def generateSliceData(zdelta):
    (facets, zmax) = Parser.parse(filename, zdelta)

    facetdata = {}
    for z in range(ceil(zmax/zdelta), 0):
        z = z * zdelta
       # triangles = []
        lines = []
        for facet in facets:
        #    if facet.isExactlyFlat(zdelta):
        #        triangles.add(facet)
       #     else:
            intersection = facet.getIntersectionLine(z)
            if intersection is not None:
                lines.add(facet.getIntersectionLine(z))
        facetdata[z] = lines
    return facetdata

def intersections(coord, layerdata, flip):
    points = []
    for ((x1, y1), (x2, y2)) in layerdata:
        if flip:
            t1 = x1
            x1 = y1
            y1 = t1
            t2 = x2
            x2 = y2
            y2 = t2
        if (x1<= coord and coord <= x2):
            if x1==x2:
                continue
            points.add((((coord-x1)*y1) + ((x2-coord)*y2))/(x1-x2))
        elif (x2<=coord and coord<=x1):
            if x2==x1:
                continue
            points.add((((coord-x2)*y2) + ((x1-coord)*y1))/(x2-x1))
    return makePairs(points.sort())

def findXYMax(facetdata):
    #Assuming all STL coords are positive, as per STL spec
    xmax = 0
    ymax = 0
    for layerdata in facetdata:
        for ((x1, y1), (x2, y2)) in layerdata:
            xmax = max(x1, x2, xmax)
            ymax = max(y1, y2, ymax)
    return (xmax, ymax)


def makePairs(points):
    if points==[]:
        return []
    return makePairs(points[2:]).addFirst((points[0], points[1]))

def getXLineSurfaceDiffs(coord, layerdata1, layerdata2, flip):
    #IGNORE TRIANGLES WOOOOOOOOT
    if (layerdata1 is None):
        return []
    if (layerdata2 is None):
        return []
    above = intersections(coord, layerdata1, flip)
    below = intersections(coord, layerdata2, flip)
    total = intervalSetUnion(above + below)
    return intervalSetDiff(total, intervalSetIntersect(above, below))

def intervalIntersect(interval1, interval2):
    return (max(interval1.first, interval2.first), min(interval1.second, interval2.second))

def intervalUnion(interval1, interval2):
    return (min(interval1.first, interval2.first), max(interval1.second, interval2.second))

def intervalHasOverlap(interval1, interval2):
    return (interval1.first >= interval2.first and interval1.first <= interval2.second) or (interval1.second >= interval2.first and interval1.second <= interval2.second) or (interval2.first >=interval1.first and interval2.first <= interval1.second)

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
                queue.add(intervalUnion(out, interval))
                found = True
                break
        if (not found):
            output.add(interval)

#pairwise intersection
def intervalSetIntersect(intervals1, intervals2):
    temp = []
    for int1 in intervals1:
        for int2 in intervals2:
            if intervalHasOverlap(int1, int2):
                temp.add(intervalIntersect(int1, int2))

    return intervalSetUnion(temp)

def intervalDiff(base, subtracting):
    if intervalIntersect(base, subtracting):
        if (subtracting.second >= base.second) and (subtracting.first <= base.first):
            return []
        if (subtracting.second >= base.second) and (subtracting.first > base.first):
            return [(subtracting.first, base.second)]
        if (subtracting.second < base.second) and (subtracting.first <= base.first):
            return [(base.first, subtracting.second)]
        return [(base.first, subtracting.first), (subtracting.second, base.second)]
    return base

def intervalSetDiff(baseIntervals, subtracting):
    base = baseIntervals
    for sub in subtracting:
        for b in base:
            base.remove(b)
            base.add(intervalDiff(b, sub))
    return base

def getSupportAndFillIntervals(x, layerData, layerdataBelow, layerdataAbove, accumulatedAbove, flip):
    diff1 = getXLineSurfaceDiffs(x, layerData, layerDataBelow, flip)
    diff2 = getXLineSurfaceDiffs(x, layerData, layerDataAbove, flip)
    surfaceLines = intervalSetUnion(diff1 + diff2)
    supportAndFill = intervalSetDiff(accumulatedAbove, surfaceLines)
    support = intervalDiff(accumulatedAbove, supportAndFill[0::2])
    fill = supportAndFill[1::2]
    return (surfaceLines, support, fill, intervalSetUnion(accumulatedAbove + surfaceLines))

def processLayer(z, facetdata, accDataX, accDataY, zdelta, zmax, xdelta, ydelta, supportSpacing, fillSpacing, xmax, ymax):
    layerData = facetdata[z]
    layerDataAbove = facetdata[z+zdelta]
    layerDataBelow = facetdata[z-zdelta]

    for x in range(0,ceil(xmax/xdelta)):
        x = x * xdelta
        (surfaceLines, support, fill, newAccData) = getSupportAndFillIntervals(x, layerData, layerDataBelow, layerDataAbove, accDataX[x], False)
        #TODO output gcode
        accDataX[x] = newAccData

    for y in range(0,ceil(ymax/ydelta)):
        y = y * ydelta
        (surfaceLines, support, fill, newAccData) = getSupportAndFillIntervals(y, layerData, layerDataBelow, layerDataAbove, accDataY[y], True)
        #TODO output gcode
        accDataY[y] = newAccData

    
    return (accDataX, accDataY)

def processAll(xdelta, ydelta, supportSpacing, fillSpacing):
    facetData = generateFacetData(zdelta)
    accIntervalsX = {}
    accIntervalsY = {}
    (xmax, ymax) = findXYMax(facetData)
    for z in range(ceil(zmax/zdelta), 0):
        z = z * zdelta
        (accIntervalsX2, accIntervalsY2) = processLayer(z, facetData, accIntervalsX, accIntervalsY, zdelta, zmax, xdelta, ydelta, supportSpacing, fillSpacing, xmax, ymax)
        accIntervalsX = accIntervalsX2
        accIntervalsY = accIntervalsY2