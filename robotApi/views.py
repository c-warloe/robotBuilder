from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from svggen.library import allComponents, getComponent, filterComponents
from svggen.api import FoldedComponent
from svggen.api.ports import EdgePort
import copy_reg
import types
import ast
import json

def reduce_method(m):
    return (getattr, (m.__self__, m.__func__.__name__))

copy_reg.pickle(types.MethodType, reduce_method)

# Create your views here.

@api_view(['GET','POST'])
def componentList(request):
    if request.method == 'GET' or request.method == 'POST':
        data = ast.literal_eval(request.body)
        try:
            filter = [data['key']]
        except:
            filter = ["actuator","mechanical"]
        l = []
        for c in filterComponents(filter):
            l.append(c)
        response = json.dumps({"response": l})
        return HttpResponse(response, content_type="application/json")


@api_view(['GET', 'POST'])
def createComponent(request):
    """
    Create a new Component
    """
    if request.method == 'GET' or request.method == 'POST':
        fc = FoldedComponent.FoldedComponent()
        name = id(fc)
        request.session['component'] = fc
        request.session['name'] = name
        return HttpResponse('FoldedComponent {} Created'.format(name))


    return HttpResponse('Error')

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
            response = {"response": responseDict}.__str__().replace("'",'"').replace('(','[').replace(')',']')
            print "ljson"
            return HttpResponse(response, content_type="application/json")
        except:
            return HttpResponse('Error')
    return HttpResponse('Error')

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
            return HttpResponse('Connection from {}:{} to {}:{} Added to Component {}'.format(sc1,port1,sc2,port2,name))
        except KeyError:
            return HttpResponse('Error')
    return HttpResponse('Error')

@api_view(['GET'])
def make(request):
    """
    Create a new Component
    """
    if request.method == 'GET':
        try:
            fc = request.session['component']
            name = request.session['name']
            fc.make()
            response = str(extractFromComponent(fc))
            return HttpResponse(response)
        except KeyError:
            return HttpResponse('Error')
    return HttpResponse('Error')


def extractFromComponent(c):
    output = {}
    output["variables"] = [x for x in c.getVariables()]
    output["relations"] = c.getRelations()
    output["defaults"] = c.getAllDefaults()
    output["faces"] = {}
    for i in c.composables['graph'].faces:
        tdict = i.getTriangleDict()
        for vertex in range(len(tdict["vertices"])):
            try:
                tpl = tdict["vertices"][vertex]
                tdict["vertices"][vertex] = [tpl[0],tpl[1]]
                tdict["vertices"][vertex][0] = c.evalEquation(tdict["vertices"][vertex][0])
                tdict["vertices"][vertex][1] = c.evalEquation(tdict["vertices"][vertex][1])
            except:
                try:
                    tdict["vertices"][vertex][1] = c.evalEquation(tdict["vertices"][vertex][1])
                except:
                    pass
        output["faces"][i.name] = [[c.evalEquation(i.transform3D[x]) for x in range(len(i.transform3D))], tdict]
    output["edges"] = {}
    for i in c.composables['graph'].edges:
        output["edges"][i.name] = []
        for v in range(2):
            output["edges"][i.name].append([])
            for x in range(3):
                output["edges"][i.name][v].append(c.evalEquation(i.pts3D[v][x]))
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



