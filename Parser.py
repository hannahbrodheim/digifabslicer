# class for an individual point
class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__ (self):
        return "x: "+str(self.x)+" y: "+str(self.y)+" z: "+str(self.z)+"\n"

# class for an individual Facet composed of points
class Facet:
    def __init__(self, normal, v1, v2, v3):
        self.normal = normal
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3

    # does this facet lie completely within the plane
    def isFlat(self, zDiff):
        # trictly less than, not less than or equal to
        if ((abs(self.v1.z - self.v2.z) < zDiff) and (abs(self.v3.z - self.v2.z) < zDiff) 
                and (abs(self.v1.z - self.v3.z) < zDiff)):
            return True
        return False

    # subtraction for points
    def minus(self, p0, p1):
        return Point(p0.x - p1.x, p0.y - p1.y, p0.z - p1.z)

    # calculate the intersection of a line and a plane
    def calculate(self, planeNormal, planePoint, p0, p1):
        return (self.dotProduct(planeNormal, (self.minus(planePoint, p0)))/
                    (self.dotProduct(planeNormal, (self.minus(p1, p0)))))

    # dot product function for two points
    def dotProduct(self, first, second):
        return (first.x * second.x) + (first.y * second.y) + (first.z * second.z)

    # find the intersection lines of a facet and a plane
    def getIntersectionLine(self, z):
        planeNormal = Point(0,0,-1)
        planePoint = Point(0,0,z)
        points = []
        extraPoints = []
        flag = False
        flag2 = False
        flag3 = False
        # is there no intersection between the facet and the plane
        if ((max(self.v1.z, self.v2.z, self.v3.z) < z) 
            or (min(self.v1.z, self.v2.z, self.v3.z) > z)):
            return None
        # check if each edge of the facet has an intersection point in the plane
        if (((self.v1.z <= z) and (self.v2.z >= z)) or ((self.v1.z >= z) and (self.v2.z <= z))):
            try:
                result = (self.calculate(planeNormal, planePoint, self.v2, self.v1))
                points.append (((((self.v1.x - self.v2.x) * result) + self.v2.x),
                                    ((self.v1.y - self.v2.y) * result + self.v2.y)))
            except ZeroDivisionError:
                if (self.v1.z==z):
                    flag = True
                    extraPoints.append((self.v1.x, self.v1.y))
                    extraPoints.append((self.v2.x, self.v2.y))
        if (((self.v3.z <= z) and (self.v2.z >= z)) or ((self.v3.z >= z) and (self.v2.z <= z))):
            try:
                result = (self.calculate(planeNormal, planePoint, self.v2, self.v3))
                points.append (((((self.v3.x - self.v2.x) * result) + self.v2.x),
                                    ((self.v3.y - self.v2.y) * result + self.v2.y)))
            except ZeroDivisionError:
                if (self.v2.z==z):
                    flag2 = True
                    extraPoints.append((self.v2.x, self.v2.y))
                    extraPoints.append((self.v3.x, self.v3.y))
        if (((self.v1.z <= z) and (self.v3.z >= z)) or ((self.v1.z >= z) and (self.v3.z <= z))):
            try:
                result = (self.calculate(planeNormal, planePoint, self.v3, self.v1))
                points.append (((((self.v1.x - self.v3.x) * result) +self.v3.x),
                                     ((self.v1.y - self.v3.y) * result + self.v3.y)))
            except ZeroDivisionError:
                if (self.v3.z==z):
                    flag3 = True
                    extraPoints.append((self.v1.x, self.v1.y))
                    extraPoints.append((self.v3.x, self.v3.y))
        # we only want the case where there is a perfect intersection at two points
        if (len(extraPoints) == 2):
            return extraPoints
        if (len(extraPoints) >2):
            return None
        if (points[0]==points[1]):
            return None
        return points

    def __str__ (self):
        return ("normal: " + str(self.normal) + " v1: " +
                    str(self.v1) + " v2: " + str(self.v2) + " v3: " + str(self.v3))

def parse(filename, zDiff):
    f = open(filename, "r")
    name = f.readline()
    next = f.readline()
    facets = []
    # slightly janky way to find the mins and maxes but within reason it should work
    maxz = -99
    minz = 99
    maxy = -99
    miny = 99
    maxx = -99
    minx = 99
    while (not next[:8] == "endsolid"):
        normal = next[15:-1].split(" ")
        f.readline() # outer loop
        v1 = f.readline()[13:-1].split(" ")
        v2 = f.readline()[13:-1].split(" ")
        v3 = f.readline()[13:-1].split(" ")
        maxz = max(maxz, float(v1[2]), float(v2[2]), float(v3[2]))
        maxy = max(maxy, float(v1[1]), float(v2[1]), float(v3[1]))
        maxx = max(maxx, float(v1[0]), float(v2[0]), float(v3[0]))
        minz = min(minz, float(v1[2]), float(v2[2]), float(v3[2]))
        miny = min(miny, float(v1[1]), float(v2[1]), float(v3[1]))
        minx = min(minx, float(v1[0]), float(v2[0]), float(v3[0]))
        # add each facet to a list of facets
        facets.append(Facet(Point(float(normal[0]), float(normal[1]), float(normal[2])), 
                            Point(float(v1[0]), float(v1[1]), float(v1[2])),
                            Point(float(v2[0]), float(v2[1]), float(v2[2])), 
                            Point(float(v3[0]), float(v3[1]), float(v3[2]))))
        f.readline() # endloop
        f.readline() # end facet
        next = f.readline() # facet
    return facets, minx, maxx, miny, maxy, minz, maxz
