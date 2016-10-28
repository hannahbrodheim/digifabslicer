class Point:
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

class Facet:
	def __init__(self, normal, v1, v2, v3):
		self.normal = normal
		self.v1 = v1
		self.v2 = v2
		self.v3 = v3

# Parser reads in the file
# returns a list of facets
# Facet class can check if the facet is flat
def parser():
