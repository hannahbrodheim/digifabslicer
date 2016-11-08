'''
M101 - extruder on, forward
M103 - extruder off
G28 - home the head
G29- do autoleveling
G1 arguments 
- x distance X100
- y distance Y100
- z distance Z100
- extruded quantity E10 (total while moving)
- feedrate per minute F100

M207 - set amount to retract filament
G10 - does what M207 says
'''
import math

class GCodeWriter:
<<<<<<< HEAD
    starterCode = "M109 S205.000000\nG28 X0 Y0 Z0 \nG92 E0 \nG29\nM207 S0.5\n"
=======
    # printrbot start and end code
    starterCode = "M109 S205.000000\nG28 X0 Y0 Z0 \nG92 E0 \nG29\nM207 S0.5\nM101\n"
>>>>>>> 5cdc4f0e6f068d6e8d2236f7c4dea41d13c354e3
    endCode = "M104 S0\nM140 S0\nG91\nG1 E-1 F300\nG28 X0 Y0\nM84\nG90\n"
    def __init__(self, filename, zDelta):
        self.f = open(filename, "w")
        self.x = 0
        self.y = 0
        self.z = 0
        self.e = 0
        self.zDelta = zDelta
        self.f.write(self.starterCode)

    # distance between two coordinates
    def distance(self, x, y, x1, y1):
        dist = math.sqrt(float(x - x1)**2 + float(y - y1)**2)
        return dist

    # extrusion quantity is just the distance times 5
    # this was chosen essentially at random
    def calculateE(self, x, y, x1, y1):
        dist = 2*self.distance(x, y, x1, y1)
        self.e = self.e + dist
        return str(self.e)

    # write a line of gcode precisely between two coordinates
    def writeDefinite(self, (x1, y1), (x2, y2)):
        a = ""#G10\n"
        a += "G1 X"+str(x1)+" Y"+str(y1)+" Z"+str(self.z)+" E"+str(self.e)+"\n"
        a += "M101\n"
        a += "G1 X"+str(x2)+" Y"+str(y2)+" Z"+str(self.z)+" E"+self.calculateE(x1, y1, x2, y2)+"\n"
        a += "M103\n"
        self.x = x2
        self.y = y2
        self.f.write(a)

    # write gcode for the line, start at the point closer to ourself
    def writeMaybe(self, (x, y), (x1, y1)):
        if (self.distance(self.x, self.y, x1, y1) < self.distance(self.x, self.y, x,y)):
            self.writeDefinite((x1,y1),(x,y))
        else:
            self.writeDefinite((x,y),(x1,y1))

    # essentially the same as the above two put into one method
    def writeLayer(self, (x1, y1), (x2, y2)):
        if(self.x == x1 and self.y == y1):
            a = "G1 X"+str(x2)+" Y"+str(y2)+" Z"+str(self.z)+" E"+self.calculateE(self.x, self.y,x2, y2)+"\n"
            self.x = x2
            self.y = y2
        elif(self.x == x2 and self.y == y2):
            a = "G1 X"+str(x1)+" Y"+str(y1)+" Z"+str(self.z)+" E"+self.calculateE(self.x, self.y,x1, y1)+"\n"
            self.x = x1
            self.y = y1
        elif (self.distance(self.x, self.y, x1, y1) < self.distance(self.x, self.y, x2, y2)):
            a = ""#G10\n"
            a += "M103\n"
            a += "G1 X"+str(x1)+" Y"+str(y1)+" Z"+str(self.z)+" E"+str(self.e)+"\n"
            a += "G1 X"+str(x2)+" Y"+str(y2)+" Z"+str(self.z)+" E"+self.calculateE(x1, y1, x2, y2)+"\n"
            a += "M101\n"
            self.x = x2
            self.y = y2
        else:
            a = ""#"G10\n"  
            a += "M103\n"
            a += "G1 X"+str(x2)+" Y"+str(y2)+" Z"+str(self.z)+" E"+str(self.e)+"\n"
            a += "G1 X"+str(x1)+" Y"+str(y1)+" Z"+str(self.z)+" E"+self.calculateE(x1, y1, x2, y2)  +"\n"
            a += "M101\n"
            self.x = x1
            self.y = y1
        self.f.write(a)

    # move up our zaxis
    def incrementLayer(self):
        self.z += self.zDelta
        a = ""#"G10\n"
        #a += "M103\n"
        a += "G1 X"+str(self.x) +" Y"+str(self.y) +" Z"+str(self.z)+"\n"
        #a += "M101\n"
        self.f.write(a)
        
    # only called once
    # write the last lines of gcode and close the file
    def done(self):
        self.f.write(self.endCode)
        self.f.close()
