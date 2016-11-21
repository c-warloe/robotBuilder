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
import traceback
import copy
import json
import pdb
from sympy import evalf

def reduce_method(m):
    return (getattr, (m.__self__, m.__func__.__name__))

copy_reg.pickle(types.MethodType, reduce_method)

# Create your views here.

@api_view(['GET','POST'])
def componentList(request):
    '''
    Returns a list of the avaliable components with their interfaces
    '''
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
        sessionComponent = FoldedComponent.FoldedComponent() #Create component
        name = id(sessionComponent)
        try:
            #Delete old components stored in session if they still exist
            del request.session['component']
        except:
            pass

        #Store session component
        request.session['component'] = sessionComponent
        return HttpResponse('FoldedComponent {} Created'.format(name))


    return HttpResponse(status=501)

@api_view(['GET', 'POST'])
def addSubcomponent(request):
    """
    Add subcomponent to component
    """
    if request.method == 'GET' or request.method == 'POST':
        try:
            #pdb.set_trace()
            #Get arguments from HTTP request
            data = ast.literal_eval(request.body)
            scname = data['name']
            type = data['type']

            #Add the subcomponent to the session component
            sessionComponent = request.session['component']
            sessionComponent.addSubcomponent(scname,type)

            #Return information about subcomponent
            c = getComponent(type)
            responseDict = extractFromComponent(c)
            print responseDict
            response = compDictToJSON(responseDict, c)
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
            fc.makeOutput(placeOnly=True)
            #print fc.__dict__
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
            traceback.print_exc()
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
            traceback.print_exc()
            return HttpResponse(status=611)
    return HttpResponse(status=611)


def extractFromComponent(c):
    output = {}
    output["variables"] = [x.name for x in c.getVariables()]
    #output["relations"] = c.getRelations()
    output["defaults"] = c.getAllDefaults()
    output["faces"] = {}
    for i in c.composables['graph'].faces:
        tdict = copy.deepcopy(i.getTriangleDict())
        for vertex in range(len(tdict["vertices"])):
            try:
                tpl = tdict["vertices"][vertex]
                tdict["vertices"][vertex] = [tpl[0], tpl[1]]
                tdict["vertices"][vertex][0] = str(tdict["vertices"][vertex][0].subs(c.getVariableSubs()))
                tdict["vertices"][vertex][1] = str(tdict["vertices"][vertex][1].subs(c.getVariableSubs()))
            except:
                try:
                    tdict["vertices"][vertex][1] = str(tdict["vertices"][vertex][1].subs(c.getVariableSubs()))
                except:
                    pass
        output["faces"][i.name] = [[str(i.transform3D[x].subs(c.getVariableSubs())) for x in range(len(i.transform3D))], tdict]
        print i.transform2D.tolist()
        trans2D = [[str(p.subs(c.getVariableSubs())) for p in j] for j in i.transform2D.tolist()]
        print trans2D
        output["faces"][i.name].append(trans2D)
    output["edges"] = {}
    for i in c.composables['graph'].edges:
        output["edges"][i.name] = []
        for v in range(2):
            output["edges"][i.name].append([])
            for x in range(3):
                try:
                    output["edges"][i.name][v].append(str(i.pts3D[v][x].subs(c.getVariableSubs())))
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

def compDictToJSON(responseDict, component):
    responseDict['parameters'] = {}
    for key in component.parameters.keys():
        responseDict['parameters'][key] = component.parameters[key].__str__()

    responseDict['variables'] = []

    return {"response": responseDict}.__str__().replace("'", '"').replace('(', '[').replace(')', ']').replace(
        'False', '0').replace('True', '1')




