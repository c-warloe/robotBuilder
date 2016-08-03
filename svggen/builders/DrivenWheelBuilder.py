from svggen.api.component import Component


self = Component()

self.addSubcomponent("servo", "Servo", continuous=True)
self.addSubcomponent("wheel", "Wheel", n=6)

self.addConnection(("servo", "shaft"),
                   ("wheel", "origin"))

self.inheritAllInterfaces("servo", prefix=None)
self.inheritAllInterfaces("wheel", prefix=None)
self.toYaml("library/DrivenWheel.yaml")
