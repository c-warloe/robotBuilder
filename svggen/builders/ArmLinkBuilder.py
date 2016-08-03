from svggen.api.component import Component
from svggen.api.Function import Function


self = Component()

# Subcomponents used in this assembly
self.addSubcomponent("beam", "Rectangle")
self.addSubcomponent("servo", "ServoDevice")
self.addSubcomponent("horn", "HornMount")

l = self.addParameter("length", 100)
w = self.addParameter("width", 25)

s = self.getComponent("servo")

self.setSubParameter(("beam", "l"), w)
self.setSubParameter(("beam", "w"), l + 2*s.getParameter('shoulderlength') + 2*s.getParameter('hornoffset'))
self.setSubParameter(("horn", "sep"), 2*s.getParameter('hornlength'))

self.addConnection(("beam", "face"),
                   ("horn", "mount"), offset_dx=0, offset_dy = "length/2")

self.addConnection(("beam", "face"),
                   ("servo", "mount"), offset_dx=0, offset_dy = "-length/2")

self.inheritInterface("input", ("servo", "input"))
self.inheritInterface("servo", ("servo", "shaft"))
self.inheritInterface("horn", ("horn", "horn"))

self.toYaml("library/ArmLink.yaml")
