import Tkinter as tk
import copy
import svgwrite
import math
import svggen.utils.mymath as np
class Unfolder(object):


    class Tree(object):
        def __init__(self):
            self.nodes={}
            self.connections = []
            self.maxX = 0
            self.maxY = 0
            self.minX = 0
            self.minY = 0

        def noCollision(self, position):
            for r in self.nodes.keys():
                rPosition = self.nodes[r]["position"]
                if rPosition["x1"] >= position["x2"] or rPosition["x2"] <= position["x1"]:
                    continue
                if rPosition["y1"] >= position["y2"] or rPosition["y2"] <= position["y1"]:
                    continue
                return False
            return True



        def placeAbove(self, reference, length):
            newLeft = (reference[0], reference[1] + length)

            def placer(side, length, width):
                if side is "b":
                    return (newLeft, 0,
                            {"b": None, "r": self.placeRight(newLeft, width), "t": self.placeAbove(newLeft, length),
                             "l": self.placeLeft(newLeft)})
                elif side is "t":
                    return ((newLeft[0]+width,newLeft[1]+length), math.pi,
                            {"t": None, "l": self.placeRight(newLeft, width), "b": self.placeAbove(newLeft, length),
                             "r": self.placeLeft(newLeft)})
                elif side is "r":
                    return ((newLeft[0],newLeft[1]+width), (-0.5)*math.pi,
                            {"r": None, "t": self.placeRight(newLeft, length), "l": self.placeAbove(newLeft, width),
                             "b": self.placeLeft(newLeft)})
                elif side is "l":
                    return ((newLeft[0]+length,newLeft[1]), 0.5*math.pi,
                            {"l": None, "b": self.placeRight(newLeft, length), "r": self.placeAbove(newLeft, width),
                             "t": self.placeLeft(newLeft)})

            return placer

        def placeBelow(self, reference):
            def placer(side, length, width):
                if side is "t":
                    newRef = (reference[0],reference[1]-length)
                    return (newRef, 0,
                            {"b": self.placeBelow(newRef), "r": self.placeRight(newRef, width), "t": None,
                             "l": self.placeLeft(newRef)})
                elif side is "b":
                    newRef = (reference[0]+width, reference[1])
                    newLeft = (reference[0], reference[1] - length)
                    return (newRef, math.pi,
                            {"t": self.placeBelow(newLeft), "l": self.placeRight(newLeft, width), "b": None,
                             "r": self.placeLeft(newLeft)})
                elif side is "l":
                    newRef = (reference[0], reference[1])
                    newLeft = (reference[0], reference[1] - width)
                    return (newRef, (-0.5)*math.pi,
                            {"r": self.placeBelow(newLeft), "t": self.placeRight(newLeft, length), "l": None,
                             "b": self.placeLeft(newLeft)})
                elif side is "r":
                    newRef = (reference[0]+length, reference[1]-width)
                    newLeft = (reference[0], reference[1] - width)
                    return (newRef, 0.5*math.pi,
                            {"l": self.placeBelow(newLeft), "b": self.placeRight(newLeft, length), "r": None,
                             "t": self.placeLeft(newLeft)})

            return placer

        def placeLeft(self, reference):
            def placer(side, length, width):
                if side is "r":
                    newRef = (reference[0]-width, reference[1])
                    return (newRef, 0,
                            {"b": self.placeBelow(newRef), "r": None,
                             "t": self.placeAbove(newRef, length),
                             "l": self.placeLeft(newRef)})
                elif side is "l":
                    newLeft = (reference[0] - width, reference[1])
                    newRef = (reference[0], reference[1]+length)
                    return (newRef, math.pi,
                            {"t": self.placeBelow(newLeft), "l": None,
                             "b": self.placeAbove(newLeft, length),
                             "r": self.placeLeft(newLeft)})
                elif side is "t":
                    newLeft = (reference[0] - length, reference[1])
                    newRef = (reference[0] - length, reference[1]+width)
                    return (newRef, (-0.5)*math.pi,
                            {"r": self.placeBelow(newLeft), "t": None,
                             "l": self.placeAbove(newLeft, width),
                             "b": self.placeLeft(newLeft)})
                elif side is "b":
                    newLeft = (reference[0] - length, reference[1])
                    newRef = reference
                    return (newRef, 0.5*math.pi,
                            {"l": self.placeBelow(newLeft), "b": None,
                             "r": self.placeAbove(newLeft, width),
                             "t": self.placeLeft(newLeft)})

            return placer

        def placeRight(self, reference, width):
            newLeft = (reference[0]+width, reference[1])

            def placer(side, length, width):
                if side is "l":
                    return (newLeft, 0,
                            {"b": self.placeBelow(newLeft), "r": self.placeRight(newLeft, width),
                             "t": self.placeAbove(newLeft, length),
                             "l": None})
                elif side is "r":
                    newRef = (newLeft[0]+width,newLeft[1]+length)
                    return (newRef, math.pi,
                            {"t": self.placeBelow(newLeft), "l": self.placeRight(newLeft, width),
                             "b": self.placeAbove(newLeft, length),
                             "r": None})
                elif side is "b":
                    newRef = (newLeft[0],newLeft[1]+width)
                    return (newRef, (-0.5)*math.pi,
                            {"r": self.placeBelow(newLeft), "t": self.placeRight(newLeft, length),
                             "l": self.placeAbove(newLeft, width),
                             "b": None})
                elif side is "t":
                    newRef = (newLeft[0]+length,newLeft[1])
                    return (newRef, 0.5*math.pi,
                            {"l": self.placeBelow(newLeft), "b": self.placeRight(newLeft, length),
                             "r": self.placeAbove(newLeft, width),
                             "t": None})

            return placer

        def add(self,rectangle, connection = None):
            existing = self.nodes.keys()
            if connection:
                if connection[0][0] not in existing:
                    return False
                placer = self.nodes[connection[0][0]]["placers"][connection[0][1]]
                if placer is None:
                    return False
                place = placer(connection[1][1], rectangle["length"], rectangle["width"])
                reference, theta, placers = place
            else:
                reference = (0,0)
                theta = 0
                placers = {"b":self.placeBelow(reference),"r":self.placeRight(reference,rectangle["width"]),"t":self.placeAbove(reference,rectangle["length"]),"l": self.placeLeft(reference)}
            transform2d = np.Matrix([[math.cos(theta), -math.sin(theta), reference[0]],
                                     [math.sin(theta),  math.cos(theta), reference[1]],
                                     [      0        ,        0        ,     1       ]])
            vertices = np.Matrix([[0,rectangle["width"]],
                                  [0,rectangle["length"]],
                                  [1,     1      ]])
            posMatrix = transform2d * vertices
            x1 = min(posMatrix[0],posMatrix[1])
            x2 = max(posMatrix[0],posMatrix[1])
            y1 = min(posMatrix[2],posMatrix[3])
            y2 = max(posMatrix[2],posMatrix[3])
            position = {"x1":x1, "x2":x2, "y1":y1, "y2":y2}
            if self.noCollision(position):
                self.nodes[rectangle["name"]] = {"position": position, "placers": placers, "transform2d":transform2d, "vertices":vertices}
                connections = [x for x in rectangle["connections"] if x[1][0] not in existing]
                self.connections = connections + self.connections
                try:
                    self.connections.remove(connection)
                except ValueError:
                    #Connection was not in connections, no need to remove
                    pass
                self.maxX = max(x2, self.maxX)
                self.maxY = max(y2, self.maxY)
                self.minX = min(x1, self.minX)
                self.minY = min(y1, self.minY)
                return True
            return False
        def getTransform2d(self, name):
            try:
                transform2d = self.nodes[name]["transform2d"]
                return transform2d
            except KeyError:
                transform2d = np.eye(3)
                return transform2d
        def drawToTkinter(self):
            master = tk.Tk()
            padding = 25
            drawingWidth = self.maxX-self.minX
            drawingHeight = self.maxY-self.minY
            windowWidth =  max(drawingWidth,100)  + (2*padding)
            windowHeight = max(drawingHeight,100) + (2*padding)
            w = tk.Canvas(master, width=windowWidth, height=windowHeight)
            w.pack()
            xOffset = padding - self.minX
            yOffset = padding - self.minY
            for r in self.nodes.keys():
                pos = self.nodes[r]["position"]
                w.create_rectangle(pos["x1"]+xOffset, pos["y1"]+yOffset, pos["x2"]+xOffset, pos["y2"]+yOffset, fill="#ABEAFF")
        def drawToSVG(self, fileprefix=None):
            if fileprefix is None:
                filename = "test.svg"
            else:
                pass
            file = svgwrite.Drawing()

    def __init__(self):
        self.tree = None
        self.makeQueue = {}
    def addRectangle(self, name, length, width, t=None, b=None, l=None, r=None):
        possibleConnections = [((name,"t"),t),((name,"b"),b),((name,"l"),l),((name,"r"),r)]
        connections = [x for x in possibleConnections if x[1]]
        self.makeQueue[name] = {"name":name, "length":length, "width":width, "connections":connections}
    def addConnection(self, connection):
        name1, connect1 = connection[0]
        name2, connect2 = connection[1]
        try:
            rect1 = self.makeQueue[name1]
            rect2 = self.makeQueue[name2]
            rect1["connections"] += [connection]
            rect2["connections"] += [(connection[1], connection[0])]
            return True
        except KeyError:
            return False

    def getTransform2d(self, name):
        if self.tree:
            return self.tree.getTransform2d(name)
        else:
            return np.eye(3)
    def getAllTransform2d(self):
        if self.tree:
            transforms ={}
            for n in self.tree.nodes.keys():
                transforms[n] = self.tree.nodes[n]["transform2d"]
            return transforms
        else:
            return {}
    def unfold(self):
        self.tree, success = self.makeTree()
        if success:
            pass
            #self.tree.drawToTkinter()
        return success
    def makeTree(self, parent=None):
        if self.makeQueue.__len__() == 0:
            tree = parent or self.Tree()
            return (tree, True)
        if parent is None:
            child = self.Tree()
            name, rectangle = self.makeQueue.popitem()
            child.add(rectangle)
        else:
            child = copy.deepcopy(parent)
        for c in child.connections:
            name = c[1][0]
            if name in self.makeQueue.keys() and child.add(self.makeQueue[name],c):
                added = self.makeQueue.pop(name)
                tree, success = self.makeTree(child)
                if success:
                    return (tree, success)
                self.makeQueue[added["name"]] = added

        return (child, self.makeQueue.__len__() == 0)










