from collections import OrderedDict
from os.path import join
import sys

import yaml
import copy
import svggen.utils.mymath as math

from svggen import SVGGEN_DIR
from svggen.api.Parameterized import Parameterized
from svggen.utils.utils import prefix as prefixString
from svggen.utils.utils import tryImport
#from svggen.utils import solver
from svggen.utils.io import load_yaml
from svggen.api import unfolder
from sympy import Symbol, Eq, StrictGreaterThan, GreaterThan, StrictLessThan, LessThan
from svggen.api.ports.Port import Port

def getSubcomponentObject(component, baseclass, name=None, **kwargs):
    try:
        obj = tryImport(component, component)
        # XXX hack to get around derived components not having name parameter in their __init__
        c = obj(**kwargs)
        c.setName(name)
        return c
    except ImportError:
        try:
            obj = tryImport(baseclass, baseclass)
            c = obj(component, **kwargs)
            c.setName(name)
            return c
        except ImportError:
            c = Component(component, **kwargs)
            c.setName(name)
            return c


class Component(Parameterized):
    def __init__(self, yamlFile=None, **kwargs):
        Parameterized.__init__(self)

        self.subcomponents = {}
        self.connections = []
        self.interfaces = {}
        self._prefixed = {}
        self.composables = OrderedDict()

        if yamlFile:
            self._fromYaml(yamlFile)

        # Override to define actual component
        self.define(**kwargs)

        self.make()

    def _make_test(self, protobuf=False, display=True):
        if not hasattr(self, '_test_params'):
            raise NotImplementedError

        for key, val in self._test_params.iteritems():
            self.setParameter(key, val)

        name = self.__class__.__name__
        self.makeOutput('output/%s' % name,
                        protobuf=protobuf,
                        display=display)

    def _strToSympy(self, s):
        expr = math.sympify(s)
        subs = []
        for a in expr.atoms(math.Symbol):
          subs.append((a, self.getParameter(repr(a))))
        expr = expr.subs(subs)
        return expr

    def _fromYaml(self, filename):
        definition = load_yaml(filename)

        # keys are (parameters, constants, subcomponents, constraints, connections, interfaces)
        try:
          for name, default in definition["parameters"].iteritems():
            self.addParameter(name, default)
        except AttributeError: pass

        try:
          for name, default in definition["constants"].iteritems():
            self.addConstant(name, default)
        except AttributeError: pass

        try:
          for name, value in definition["subcomponents"].iteritems():
            try: 
              # XXX Can these be sympy functions as well?
              kwargs = value["constants"]
            except AttributeError:
              kwargs = {}
            self.addSubcomponent(name, value["class"], **kwargs)
            try:
              for param, pvalue in value["parameters"].iteritems():
                self.addParameterConstraint((name, param), self._strToSympy(pvalue))
            except AttributeError:
              pass
        except AttributeError: pass

        try:
          for value in definition["constraints"]:
            self.addSemanticConstraint(self._strToSympy(value))
        except AttributeError: pass

        try:
          for toPort, fromPort, kwargs in definition["connections"]:
            for param, pvalue in kwargs.iteritems():
                kwargs[param] = self._strToSympy(pvalue)
            self.addConnection(toPort, fromPort, **kwargs)
        except AttributeError: pass

        try:
          for name, value in definition["interfaces"].iteritems():
            self.inheritInterface(name, (value["subcomponent"], value["interface"]))
        except AttributeError: pass

    def define(self, **kwargs):
        ### Override to define interfaces
        pass

    ###
    # DESIGN PHASE
    ###

    def addSubcomponent(self, name, obj, **kwargs):
        '''
        :param name: unique identifier to refer to this component by
        :type  name: str or unicode
        :param obj: code name of the subcomponent
                    should be python file/class or yaml name
        :type  obj: str or unicode
        '''
        # XXX will silently fail if subcomponent name is already taken?
        sc = {"class": obj, "parameters": {}, "constants": kwargs, "baseclass": "Component", "component": None}
        self.subcomponents.setdefault(name, sc)
        self.resolveSubcomponent(name)

        '''
        if inherit:
            if prefix == "":
                prefix = name

            obj = getComponent(name)
            for key, value in obj.parameters.iteritems():
                # inherit = True : inherit all parameters
                if inherit is True or key in inherit:
                    try:
                        self.addParameter(prefixString(prefix, key), value)
                    except KeyError:
                        # It's ok if we try to add a parameter that already exists
                        pass
                    self.addConstraint((name, key), prefixString(prefix, key))
            # XXX also inherit interfaces?
        '''

    def delSubcomponent(self, name):
        toDelete = []

        # delete edges connecting components
        for i, ((fromComp, _), (toComp, _), _) in enumerate(self.connections):
            if name in (fromComp, toComp):
                toDelete.append(i)
        for i in reversed(toDelete):
            self.connections.pop(i)
        if self.subcomponents[name]['component'] and 'graph' in self.subcomponents[name]['component'].composables:
            self.subcomponents[name]['component'].composables['graph'].splitMergedEdges()
        self.subcomponents.pop(name)
        del self.composables['graph']
        if name in self._prefixed:
            del self._prefixed[name]
        for sc in self.subcomponents:
            if 'graph' in self.subcomponents[sc]['component'].composables:
                self.subcomponents[sc]['component'].composables['graph'].placed = False

    def addParameterConstraint(self, (subComponent, parameterName), constr):
        self.subcomponents[subComponent]["parameters"][parameterName] = constr

    def addInterface(self, name, val):
        if name in self.interfaces:
            raise ValueError("Interface %s already exists" % name)
        self.interfaces.setdefault(name, val)
        return self

    def delInterface(self, name):
        self.interfaces.pop(name)

    def inheritAllInterfaces(self, subcomponent, prefix=""):
        self.resolveSubcomponent(subcomponent)
        obj = self.getComponent(subcomponent)
        if prefix == "":
          prefix = name

        for name, value in obj.interfaces.iteritems():
          if name in self.interfaces:
            raise ValueError("Interface %s already exists" % name)
          self.interfaces.setdefault(prefixString(prefix, name), {"subcomponent": subcomponent, "interface": name})
        return self

    def inheritInterface(self, name, (subcomponent, subname)):
        if name in self.interfaces:
            raise ValueError("Interface %s already exists" % name)
        self.interfaces.setdefault(name, {"subcomponent": subcomponent, "interface": subname})
        return self

    def addConnection(self, fromInterface, toInterface, **kwargs):
        self.connections.append([fromInterface, toInterface, kwargs])

    def addTabConnection(self, fromInterface, toInterface, **kwargs):
        kwargs['tab'] = True
        self.connections.append([fromInterface, toInterface, kwargs])

    '''
    # TODO : delete Connection
    # TODO : remove constraints that involve this parameter?
    def delParameter(self, name):
    '''

    def toYaml(self, filename=None):
        parameters = {}
        constants = {}
        for k, v in self.parameters.iteritems():
            if isinstance(v, math.Symbol):
              parameters[k] = self.getVariableValue(k)
            else:
              constants[k] = v

        subcomponents = {}
        for k, v in self.subcomponents.iteritems():
          subparams = {}
          for param, value in v["parameters"].iteritems():
            try:
              value = repr(value.subs(self.getAllSubs()))
            except AttributeError:
              pass
            subparams[param] = value
          subcomponents[k] = {"class": v["class"], "parameters": subparams, "constants": v["constants"]}

        constraints = []
        for x in self.localSemanticConstraints:
          expr = repr(x.subs(self.getAllSubs()))
          constraints.append(expr)

        connections = []
        for toPort, fromPort, kwargs in self.connections:
          newArgs = {}
          for param, value in kwargs.iteritems():
            try:
              value = repr(value.subs(self.getAllSubs()))
            except AttributeError:
              pass
            newArgs[param] = value
          connections.append([toPort, fromPort, newArgs])

        definition = {
            "parameters" : parameters,
            "constants" : constants,
            "subcomponents" : subcomponents,
            "constraints" : constraints,
            "connections" : connections,
            "interfaces" : self.interfaces,
        }

        if filename is not None:
            with open(join(SVGGEN_DIR, filename), "w") as fd:
                yaml.safe_dump(definition, fd)
        else:
            return yaml.safe_dump(definition)

    ###
    # GETTERS AND SETTERS
    ###
    def getDefaults(self):
        defs = {}
        for n in self.parameters:
            defs[n] = self.getVariableValue(n)
        return defs

    def getAllDefaults(self):
        mydefs = self.getDefaults()
        if len(self.subcomponents) == 0:
            return self.getDefaults()
        defs = copy.deepcopy(mydefs)
        for s in self.subcomponents:
            subDefs = self.subcomponents[s]["component"].getAllDefaults()
            for k,v in subDefs.iteritems():
                defs[prefixString(s,k)] = v
        return defs
        
    def getComponent(self, name):
        return self.subcomponents[name]["component"]

    def setSubParameter(self, (c, n), v):
        self.subcomponents[c]["parameters"][n] = v

    def getInterfaces(self, component, name):
        return self.getComponent(component).getInterface(name)

    def getInterface(self, name):
        c = self.interfaces[name]

        if isinstance(c, dict):
            subc = c["subcomponent"]
            subi = c["interface"]
            return self.getInterfaces(subc, subi)
        else:
          return c

    def setInterface(self, n, v):
        if n in self.interfaces:
            self.interfaces[n] = v
        else:
            raise KeyError("Interface %s not initialized" % n)
        return self

    ###
    # ASSEMBLY PHASE
    ###

    def assemble(self):
        ### Override to combine components' drawings to final drawing
        pass

    def append(self, name, prefix):
        component = self.getComponent(name)

        allPorts = set()
        if 'graph' in component.composables:
            for face in component.composables['graph'].faces:
                face.updateSubs(self.subs.values())
            for edge in component.composables['graph'].edges:
                edge.updateSubs(self.subs.values())
        for key in component.interfaces:
          ports = component.getInterface(key)
          if isinstance(ports, Port):
              allPorts.add(component.getInterface(key))
              if name not in self._prefixed:
                  ports.prefix(prefix)
              ports.update()
          else:
              allPorts.update(component.getInterface(key))
              for port in ports:
                  if name not in self._prefixed:
                      port.prefix(prefix)
                  port.update()
        for (key, composable) in component.composables.iteritems():
            if name not in self._prefixed:
                composable.prefixed = False
            else:
                composable.prefixed = True
            self.composables[key].append(composable, prefix)
        self._prefixed[name] = component

    def attach(self, (fromName, fromPort), (toName, toPort), **kwargs):
        interface1 = self.getInterfaces(fromName, fromPort)
        interface2 = self.getInterfaces(toName, toPort)

        # Interfaces can contain multiple ports, so try each pair of ports
        if not isinstance(interface1, (list, tuple)):
          interface1 = [interface1]
        if not isinstance(interface2, (list, tuple)):
          interface2 = [interface2]
        if len(interface1) != len(interface2):
          if len(interface1) == 1:
            interface1 = interface1 * len(interface2)
          elif len(interface2) == 1:
            interface2 = interface2 * len(interface1)
          else:
            raise AttributeError("Number of ports in each interface don't match")

        for (port1, port2) in zip(interface1, interface2):
          self.extendSemanticConstraints(port1.constrain(self, port2, **kwargs))
          for (key, composable) in self.composables.iteritems():
            try:
                composable.attach(port1, port2, **kwargs)
            except:
                print "Error in attach:"
                print (fromName, fromPort),
                print self.getInterfaces(fromName, fromPort).toString()
                print (toName, toPort),
                print self.getInterfaces(toName, toPort).toString()
                raise

    def getSolvingBounds(self):
        lb = {}
        ub = {}
        defs = self.getAllDefaults()
        for v in defs:
            lb[v] = "-realmax"
            ub[v] = "realmax"
        return (lb,ub)

    def solve(self):
        pass

    def checkConstraints(self):
        for constraint in self.constraints:
            if self.evalEquation(constraint) == False:
                raise Exception("Constraint " + constraint.__str__() + " not satisfied.")
            else:
                pass
                #print "Constraint " + constraint.__str__() + " satisfied."


    def evalEquation(self,eqn):
        #eqnEval = eqn.xreplace(self.getAllSubs())
        #print eqn
        #x = self.allParameters.keys()
        #y = [v.getValue() for v in x]
        #try:
        #    f = lambdify(x, eqn)
        #    return f(*y)
        #except:
        #    return eqn

        d = {x: x.getValue() for x in self.allParameters.keys()}
        try:
            return eqn.evalf(subs=d)
        except:
            return eqn
        '''
        eqnEval = eqn
        for s in eqnEval.atoms(Symbol):
            #print "EQN EVAL: " + s.name + ": " + str(s.getValue())
            eqnEval = eqnEval.subs(s, s.getValue())
        return eqnEval'''

    ###
    # BUILD PHASE
    ###

    def modifyParameters(self):
        # Override to manually specify how parameters get set during build
        pass

    def resolveSubcomponents(self):
        for name in self.subcomponents:
            self.resolveSubcomponent(name)

    def resolveSubcomponent(self, name):
        sc = self.subcomponents[name]
        try:
          if sc["component"]:
            # Already resolved
            # XXX Check to see why we're calling this again?
            return
        except KeyError:
          # We're adding the component anyway, so no worries
          pass

        c = sc["class"]
        try:
          kwargs = sc["constants"]
        except KeyError:
          kwargs = {}
        obj = getSubcomponentObject(c, sc["baseclass"], name = prefixString(self.getName(), name), **kwargs)
        self.subcomponents[name]["component"] = obj
        self.inheritParameters(obj, name)
        self.inheritSemanticConstraints(obj)
        self.inheritConstraints(obj)

    def inheritSemanticConstraints(self, subComponent):
        self.extendSemanticConstraints(subComponent.getSemanticConstraints())

    def inheritConstraints(self, subComponent):
        self.extendConstraints(subComponent.getConstraints())

    def evalConstraints(self):
        for subComponent in self.subcomponents.iterkeys():
            for (parameterName, value) in self.subcomponents[subComponent]["parameters"].iteritems():
                  #XXX Should probably set value in subcomponent object
                  #self.getComponent(subComponent).setParameter(parameterName, value)
                  self.setParameter(prefixString(subComponent, parameterName), value)

    # Append composables from all known subcomponents
    # (including ones without explicitly defined connections)
    def evalComponents(self):
        for (name, sc) in self.subcomponents.iteritems():
            obj = sc["component"]
            classname = sc["class"]
            try:
                #obj.make()
                for (key, composable) in obj.composables.iteritems():
                    if key not in self.composables:
                        self.composables[key] = composable.new()
                        self.composables[key].setComponent(self)
                self.append(name, name)
            except:
                print "Error in subclass %s, instance %s" % (classname, name)
                raise
        # Let composables know what components exist
        # TODO remove this when we have a better way of letting composables
        # know about components that have no ports (ex Bluetooth module driver)
        for (key, composable) in self.composables.iteritems():
          for (name, sc) in self.subcomponents.iteritems():
            composable.addComponent(sc["component"])

    def evalInterfaces(self):
      for (name, value) in self.interfaces.iteritems():
        for (key, composble) in self.composables.iteritems():
          if value is not None:
            composble.addInterface(self.getInterface(name))

    def evalConnections(self):

        for ((fromComponent, fromPort), (toComponent, toPort), kwargs) in self.connections:
            print "kwargs"
            print kwargs
            self.attach((fromComponent, fromPort),
                        (toComponent, toPort),
                        **kwargs)

#    def evalTabs(self):
#        for ((fromComponent, fromPort), (toComponent, toPort), kwargs) in self.tabs:
#            self.attach((fromComponent, fromPort),
#                (toComponent, toPort),
#                tab = True,
#               **kwargs)

    def reset(self):
        self.semanticConstraints = []
        self.localSemanticConstraints = []

    def make(self):
        self.reset()
        self.modifyParameters()
        self.resolveSubcomponents()
        self.evalConstraints()

        self.evalComponents()    # Merge composables from all subcomponents and tell them my components exist
        self.evalInterfaces()    # Tell composables that my interfaces exist
        self.evalConnections()   # Tell composables which interfaces are connected
#        self.evalTabs()
        self.assemble()
        self.solve()
        self.checkConstraints()

        #self.unfoldComponent()

    ###
    # OUTPUT PHASE
    ###


    def unfoldComponent(self):
        uf = unfolder.Unfolder()
        faces = {}
        for r in self.getGraph().faces:
            #if type(r) is not
            name = r.name[:2]
            l = r.edgeLength(0).subs(self.getVariableSubs()).atoms(Symbol).pop()
            w = r.edgeLength(1).subs(self.getVariableSubs()).atoms(Symbol).pop()
            length = self.getVariableValue(l.name)
            width = self.getVariableValue(w.name)
            faces[name] = r
            #print name,length,width
            uf.addRectangle(name, width, length)
        for c in self.connections:
            uf.addConnection((c[0],c[1]))
        uf.unfold()
        transforms = uf.getAllTransform2d()
        for r in transforms.keys():
            faces[r].transform2D = transforms[r]


    def makeComponentHierarchy(self):
        self.resolveSubcomponents()
        hierarchy = {}
        for n, sc in self.subcomponents.iteritems():
            hierarchy[n] = {"class":sc["class"], "subtree":sub.makeComponentHierarchy()}
        return hierarchy

    def makeComponentTree(self, fn, root="Root"):
        import pydot
        graph = pydot.Dot(graph_type='graph')
        mynode = pydot.Node(root, label = root)
        self.recurseComponentTree(graph, mynode, root)
        graph.write_png(fn)

    def recurseComponentTree(self, graph, mynode, myname):
        import pydot
        self.resolveSubcomponents()
        for n, sc in self.subcomponents.iteritems():
            fullstr = myname + "/" + n
            subnode = pydot.Node(fullstr, label = sc["class"] + r"\n" + n)
            graph.add_node(subnode)
            edge = pydot.Edge(mynode, subnode)
            graph.add_edge(edge)
            sub.recurseComponentTree(graph, subnode, fullstr)

    def makeOutput(self, filedir=".", **kwargs):
        def kw(arg, default=False):
            if arg in kwargs:
                return kwargs[arg]
            return default

        print "Compiling robot designs..."
        sys.stdout.flush()
        if kw("remake", True):
            self.make()
        print "done."

        # XXX: Is this the right way to do it?
        import os
        try:
            os.makedirs(filedir)
        except:
            pass

        # Process composables in some ordering based on type
        orderedTypes = ['electrical', 'ui', 'code'] # 'code' needs to know about pins chosen by 'electrical', and 'code' needs to know about IDs assigned by 'ui'
        # First call makeOutput on the ones of a type whose order is specified
        for composableType in orderedTypes:
            if composableType in self.composables:
                self.composables[composableType].makeOutput(filedir, **kwargs)
        # Now call makeOutput on the ones whose type did not care about order
        for (composableType, composable) in self.composables.iteritems():
            if composableType not in orderedTypes:
                self.composables[composableType].makeOutput(filedir, **kwargs)

        if kw("tree"):
            print "Generating hierarchy tree... ",
            sys.stdout.flush()
            self.makeComponentTree(filedir + "/tree.png")
            print "done."
        print

        print "Happy roboting!"

    ###
    # OTHER STUFF
    ###

    def addConstant(self, name, value, **kwargs):
        value = name in kwargs and kwargs[name] or value
        Parameterized.addParameter(self, name, value, isSymbol=False)
        return value

    def toProtoBuf(self, filedir):
        from svggen.api import proto_conversion3
        from google.protobuf import text_format

        """
        print 'begin symbolicization of parameters'
        for p in self.parameters:
            print p
            self.symbolicize(p)
        """

        
        proto = proto_conversion3.componentToNewTemplateProto(self)
        text_format.PrintMessage(proto, open(filedir + '/template.asciiproto', 'w'), 2)
        open(filedir + '/template.proto', 'wb').write(proto.SerializeToString())
        self.composables['graph'].unplace()

