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
		triangles = []
		lines = []
		for facet in facets:
			if facet.isExactlyFlat(zdelta):
				triangles.add(facet)
			else 
				lines.add(facet.getIntersectionLine(z))
		facetdata[z] = (lines, triangles)
	return facetdata

def intersections(coord, layerdata):
	return [] #TODO

def getXLineSurfaceDiffs(coord, layerdata1, layerdata2):
	#IGNORE TRIANGLES WOOOOOOOOT
	above = intersections(coord, layerdata1)
	below = intersections(coord, layerdata2)
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


def getSupportAndFillIntervals(z, layerdataBelow, layerdataAbove)



def processLayer(z, facetdata, zdelta, zmax, xdelta, supportSpacing, fillSpacing):
	xmax = findXMax(facetdata[z])

	for x in range(0,ceil(xmax/xdelta)):
		x = x * xdelta
