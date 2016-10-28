class Point:
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

	def __str__ (self):
		return "x: "+str(self.x)+" y: "+str(self.y)+" z: "+str(self.z)+"\n"

class Facet:
	def __init__(self, normal, v1, v2, v3):
		self.normal = normal
		self.v1 = v1
		self.v2 = v2
		self.v3 = v3

	def isFlat(self, zDiff):
		# trictly less than, not less than or equal to
		if ((abs(self.v1.z - self.v2.z) < zDiff) and (abs(self.v3.z - self.v2.z) < zDiff) and (abs(self.v1.z - self.v3.z) < zDiff)):
			return True
		return False

	def minus(self, p0, p1):
		return Point(p0.x - p1.x, p0.y - p1.y, p0.z - p1.z)

	def calculate(self, planeNormal, planePoint, p0, p1):
		return (self.dotProduct(planeNormal, (self.minus(planePoint, p0)))/(self.dotProduct(planeNormal, (self.minus(p1, p0)))))

	def dotProduct(self, first, second):
		return (first.x * second.x) + (first.y * second.y) + (first.z * second.z)

	def getIntersectionLine(self, z):
		planeNormal = Point(0,0,1)
		planePoint = Point(0,0,z)
		points = []
		if ((max(self.v1.z, self.v2.z, self.v3.z) < z) or (min(self.v1.z, self.v2.z, self.v3.z) > z)):
			return None
		if (((self.v1.z <= z) and (self.v2.z >= z)) or ((self.v1.z >= z) and (self.v2.z <= z))):
			result = (self.calculate(planeNormal, planePoint, self.v1, self.v2))
			points.append ((((abs(self.v1.x - self.v2.x) * result) + min(self.v1.x, self.v2.x)), (abs(self.v1.y - self.v2.y) * result+ min(self.v1.y, self.v2.y))))
		if (((self.v3.z <= z) and (self.v2.z >= z)) or ((self.v3.z >= z) and (self.v2.z <= z))):
			result = (self.calculate(planeNormal, planePoint, self.v3, self.v2))
			points.append ((((abs(self.v3.x - self.v2.x) * result)+ min(self.v3.x, self.v2.x)), (abs(self.v3.y - self.v2.y) * result+ min(self.v3.y, self.v2.y))))

		if (((self.v1.z <= z) and (self.v3.z >= z)) or ((self.v1.z >= z) and (self.v3.z <= z))):
			result = (self.calculate(planeNormal, planePoint, self.v1, self.v3))
			points.append ((((abs(self.v1.x - self.v3.x) * result)+ min(self.v1.x, self.v3.x)), (abs(self.v1.y - self.v3.y) * result+ min(self.v1.y, self.v3.y))))

		return points

	def __str__ (self):
		return "normal: "+str(self.normal) +" v1: "+str(self.v1)+" v2: "+str(self.v2)+" v3: "+str(self.v3)

def parse(filename, zDiff):
	f = open(filename, "r")
	name = f.readline()
	next = f.readline()
	facets = []
	maxz = -99
	while (not next[:8] == "endsolid"):
		normal = next[15:-1].split(" ")
		f.readline() # outer loop
		v1 = f.readline()[13:-1].split(" ")
		v2 = f.readline()[13:-1].split(" ")
		v3 = f.readline()[13:-1].split(" ")
		maxz = max(maxz, v1[2], v2[2], v3[2])
		facets.append(Facet(Point(float(normal[0]), float(normal[1]), float(normal[2])), Point(float(v1[0]), float(v1[1]), float(v1[2])), Point(float(v2[0]), float(v2[1]), float(v2[2])), Point(float(v3[0]), float(v3[1]), float(v3[2]))))
		f.readline() # endloop
		f.readline() # end facet
		next = f.readline() # facet
	return facets, maxz
