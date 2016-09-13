from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from svggen.library import filterDatabase, allComponents, getComponent, filterComponents
from svggen.api import FoldedComponent
from svggen.api.ports import EdgePort
import copy_reg
import types
import ast
import json
import pdb
from sympy import evalf

def reduce_method(m):
    return (getattr, (m.__self__, m.__func__.__name__))

copy_reg.pickle(types.MethodType, reduce_method)

# Create your views here.

@api_view(['GET','POST'])
def componentList(request):
    if request.method == 'GET' or request.method == 'POST':
        '''data = ast.literal_eval(request.body)
        try:
            filter = [data['key']]
        except:
            filter = ["actuator","mechanical"]
        l = []
        for c in filterComponents(filter):
            l.append(c)
        response = json.dumps({"response": l})
        print response'''
        '''components = filterDatabase('mechanical')
        response = []
        for c in components:
            response.append([c.name, c.interfaces.keys])
        response = response.__str__().replace("'",'"')'''
        response = '{"response": [["Rectangle", ["r", "b", "l", "t"]], ["Triangle", ["a", "b", "c"]], ["Beam", ["botedge", "topedge"]], ["RectBeam", ["botedge3", "topedge2", "botedge0", "botedge1", "topedge0", "topedge1", "botedge2", "topedge3"]]]}'
        return HttpResponse(response, content_type="application/json")
    return HttpResponse(status=501)


@api_view(['GET', 'POST'])
def createComponent(request):
    """
    Create a new Component
    """

    if request.method == 'GET' or request.method == 'POST':
        fc = FoldedComponent.FoldedComponent()
        name = id(fc)
        try:
            del request.session['component']
        except:
            pass
        request.session['component'] = fc
        request.session['name'] = name
        return HttpResponse('FoldedComponent {} Created'.format(name))


    return HttpResponse(status=501)

@api_view(['GET', 'POST'])
def addSubcomponent(request):
    """
    Create a new Component
    """
    if request.method == 'GET' or request.method == 'POST':
        try:
            data = ast.literal_eval(request.body)
            fc = request.session['component']
            print "component"
            scname = data['name']
            print scname
            type = data['type']
            print type
            fc.addSubcomponent(scname,type)
            c = getComponent(type)
            print c.__str__()
            responseDict = extractFromComponent(c)
            print responseDict
            responseDict['parameters'] = {}
            for key in c.parameters.keys():
                responseDict['parameters'][key] = c.parameters[key].__str__()
            print responseDict
            responseDict['variables'] = []

            response = {"response": responseDict}.__str__().replace("'",'"').replace('(','[').replace(')',']').replace('False', '0').replace('True', '1')
            #pdb.set_trace()
            print response
            try:
                return HttpResponse(response, content_type="application/json")
            except Exception as e:
                print e.strerror
        except:
            return HttpResponse(status=501)
    return HttpResponse(status=501)

@api_view(['GET','POST'])
def addConnection(request):
    """
    Create a new Component
    """
    if request.method == 'GET' or request.method == 'POST':
        try:
            data = ast.literal_eval(request.body)
            fc = request.session['component']
            sc1 = data['sc1']
            port1 = data['port1']
            sc2 = data['sc2']
            port2 = data['port2']
            fc.addConnection((sc1,port1),(sc2,port2))
            print 'Connection from {}:{} to {}:{} Added to Component {}'.format(sc1,port1,sc2,port2,"")
            return HttpResponse('Connection from {}:{} to {}:{} Added to Component {}'.format(sc1,port1,sc2,port2,""))
        except KeyError:
            return HttpResponse(status=501)
    return HttpResponse(status=501)

@api_view(['GET','POST'])
def make(request):
    """
    Create a new Component
    """
    if request.method == 'GET' or request.method == 'POST':
        try:
            fc = request.session['component']
            print fc.__dict__
            fc.make()
            print "made"
            responseDict = extractFromComponent(fc)
            print responseDict
            responseDict['parameters'] = {}
            for key in fc.parameters.keys():
                responseDict['parameters'][key] = fc.parameters[key].__str__()
            print responseDict
            responseDict['variables'] = []
            response = {"response": responseDict}.__str__().replace("'", '"').replace('(', '[').replace(')', ']').replace('False', '0').replace('True', '1')
            print response
            return HttpResponse(response, content_type="application/json")
        except Exception as e:
            print '%s (%s)' % (e.message, type(e))
            return HttpResponse(status=501)
    return HttpResponse(status=501)

@api_view(['GET','POST'])
def getSVG(request):
    """
    Create a new Component
    """
    #pdb.set_trace()
    if request.method == 'GET' or request.method == 'POST':
        try:
            fc = request.session['component']
            #pdb.set_trace()
            svg = fc.getGraph().makeOutput(filedir=".",svgString = True)
            try:
                dim = fc.drawing.getDimensions()
                w = max(dim[1][0] - dim[0][0],10)
                h = max(dim[1][1] - dim[0][1],10)
                svg = svg[:5] + 'viewbox="0 0 ' + w.__str__() + " " + h.__str__() + '" ' + svg[5:]
            except:
                pass
            svg = svg.__str__().replace('"',"'")
            response = '{"response": "' + svg +'"}'
            print response
            return HttpResponse(response, content_type="application/json")
        except Exception as e:
            print '%s (%s)' % (e.message, type(e))
            return HttpResponse(status=611)
    return HttpResponse(status=611)


def extractFromComponent(c):
    output = {}
    output["variables"] = [x for x in c.getVariables()]
    #output["relations"] = c.getRelations()
    output["defaults"] = c.getAllDefaults()
    output["faces"] = {}
    for i in c.composables['graph'].faces:
        tdict = i.getTriangleDict()
        for vertex in range(len(tdict["vertices"])):
            try:
                tpl = tdict["vertices"][vertex]
                tdict["vertices"][vertex] = [tpl[0],tpl[1]]
                tdict["vertices"][vertex][0] = c.evalEquation(tdict["vertices"][vertex][0].evalf()).evalf()
                tdict["vertices"][vertex][1] = c.evalEquation(tdict["vertices"][vertex][1].evalf()).evalf()
            except:
                try:
                    tdict["vertices"][vertex][1] = c.evalEquation(tdict["vertices"][vertex][1].evalf()).evalf()
                except:
                    pass
        output["faces"][i.name] = [[c.evalEquation(i.transform3D[x]).evalf() for x in range(len(i.transform3D))], tdict]
    output["edges"] = {}
    for i in c.composables['graph'].edges:
        output["edges"][i.name] = []
        for v in range(2):
            output["edges"][i.name].append([])
            for x in range(3):
                try:
                    output["edges"][i.name][v].append(c.evalEquation(i.pts3D[v][x]).evalf())
                except:
                    pass
    output["interfaceEdges"] = {}
    for k,v in c.interfaces.iteritems():
        obj = c.getInterface(k)
        if isinstance(obj,EdgePort.EdgePort):
            output["interfaceEdges"][k] = []
            for i in obj.getEdges():
                try:
                    output["interfaceEdges"][k].append(i)
                except:
                    pass
    output["solved"] = c.getAllDefaults()
    return output



