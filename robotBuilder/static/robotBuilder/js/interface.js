var listURL     = "/api/component/list/"
var createURL   = "/api/component/create/"
var addScURL    = "/api/component/addSubcomponent/"
var addCnURL    = "/api/component/addConnection/"
var addTabURL    = "/api/component/addTab/"
var makeURL     = "/api/component/make/"
var svgURL      = "/api/component/svg/"
var svgDlURL    = "/api/component/download/svg/"
var fEdgeURL    = "/api/component/fixEdgeInterface/"
var cParameterURL = "/api/component/constrainParameter/"
var yamlDlURL   = "/api/component/download/yaml/"
var addParameterURL = "/api/component/addParameter/"
var delSubcomponentURL = "/api/component/delSubcomponent/"
var delParameterURL = "/api/component/delParameter/"
var delInterfaceURL = "/api/component/delInterface/"
var inheritInterfaceURL = "/api/component/inheritInterface/"
var componentSaveURL = "/api/component/save/"

function getComponentList(key, callback)
{
    httpPostAsync(listURL,"{'key': '"+key+"'}",callback);
}

function createComponent()
{
    httpPostAsync(createURL,"",function(){});
}

function addSubcomponent(name, type, callback)
{
    httpPostAsync(addScURL,"{'name': '" + name + "','type': '" + type + "'}",callback);
}

function fixComponentEdgeInterface(name, interface, value)
{
    httpPostAsync(fEdgeURL, "{'name': '" + name + "', 'interface': '" + interface + "', 'value': '" + value + "'}", function(){});
}

function addComponentConnection(sc1, port1, sc2, port2, args, callback)
{
    httpPostAsync(addCnURL,"{'sc1': '" + sc1 + "','sc2': '" + sc2 + "','port1': '" + port1 + "','port2': '" + port2 + "','angle': '" + args + "'}",callback);
}

function addTabConnection(sc1, port1, sc2, port2, args, callback)
{
    httpPostAsync(addTabURL,"{'sc1': '" + sc1 + "','sc2': '" + sc2 + "','port1': '" + port1 + "','port2': '" + port2 + "','angle': '" + args + "'}",callback);
}

function constrainParameter(sc, parameter, constr)
{
    httpPostAsync(cParameterURL, "{'sc': '" + sc + "', 'parameter': '" + parameter + "', 'constraint': '" + constr + "'}", function(){});
}

function makeComponent(callback)
{
    httpPostAsync(makeURL,"",callback);
}

function getSVG(callback)
{
    httpPostAsync(svgURL,"",callback);
}

function getSVGDownload(callback)
{
    httpPostAsync(svgDlURL,"",callback);
}

function getYamlDownload(callback)
{
    httpPostAsync(yamlDlURL,"", callback);
}

function addParameter(name, def)
{
    httpPostAsync(addParameterURL, "{'name': '" + name + "', 'def': '" + def + "'}", function(){});
}

function delSubcomponent(name)
{
    httpPostAsync(delSubcomponentURL, "{'name': '" + name + "'}", function(){});
}

function delParameter(name)
{
    httpPostAsync(delParameterURL, "{'name': '" + name + "'}", function(){});
}

function delInterface(name)
{
    httpPostAsync(delInterfaceURL, "{'name': '" + name + "'}", function(){});
}

function inheritInterface(name, scname, interface)
{
    httpPostAsync(inheritInterfaceURL, "{'name': '" + name + "', 'scname': '" + scname + "', 'interface': '" + interface + "'}", function(){});
}

function componentSave(name, callback)
{
    httpPostAsync(componentSaveURL, "{'name': '" + name + "'}", callback)
}

function httpPostAsync(theUrl, data, callback)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.responseText);
    }
    xmlHttp.open("POST", theUrl, true); // true for asynchronous
    xmlHttp.send(data);
}