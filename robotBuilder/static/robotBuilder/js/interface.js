var listURL = "/api/component/list/"
var createURL =  "/api/component/create/"
var addScURL = "/api/component/addSubcomponent/"
var addCnURL = "/api/component/addConnection/"

function  getComponentList(key, callback)
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

function addComponentConnection(sc1, port1, sc2, port2)
{
    httpPostAsync(addCnURL,"{'sc1': '" + sc1 + "','sc2': '" + sc2 + "','port1': '" + port1 + "','port2': '" + port2 + "'}",function(){});
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