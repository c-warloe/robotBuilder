var listURL     = "/api/component/list/"
var createURL   = "/api/component/create/"
var addScURL    = "/api/component/addSubcomponent/"
var addCnURL    = "/api/component/addConnection/"
var makeURL     = "/api/component/make/"
var svgURL      = "/api/component/svg/"
var svgDlURL    = "/api/component/download/svg/"
var fEdgeURL    = "/api/component/fixEdgeInterface/"
var cParameterURL = "/api/component/constrainParameter/"
var yamlDlURL   = "/api/component/download/yaml/"
var addParameterURL = "/api/component/addParameter/"

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
    httpPostAsync(fEdgeURL, "{'name': '" + name + "', 'interface': '" + interface + "', 'value': '" + value + "'}");
}

function addComponentConnection(sc1, port1, sc2, port2, args)
{
    httpPostAsync(addCnURL,"{'sc1': '" + sc1 + "','sc2': '" + sc2 + "','port1': '" + port1 + "','port2': '" + port2 + "','angle': '" + args + "'}",function(){});
}

function constrainParameter(sc, parameter, constr)
{
    httpPostAsync(cParameterURL, "{'sc': '" + sc + "', 'parameter': '" + parameter + "', 'constraint': '" + constr + "'}");
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
    httpPostAsync(addParameterURL, "{'name': '" + name + "', 'def': '" + def + "'}");
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