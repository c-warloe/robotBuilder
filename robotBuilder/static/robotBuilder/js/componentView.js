var container, svgcontainer;
var camera, svgcamera, control, orbit, scene, svgscene, renderer, svgrenderer, stl_loader, gui, rightpanel, subprops, componentName;
var subcomponents = [];
var connectedSubcomponents = [];
var componentObj;
var componentLibrary = {};
var componentMenus = {};
var parameters = {};
var interfaces = {};
var connections = [];
var tempParams = {};
var componentCount = 0;

var raycaster = new THREE.Raycaster();
raycaster.linePrecision = 3;
var mouse = new THREE.Vector2(),
    offset = new THREE.Vector3(),
    SELECTED_2, SELECTED;

$("#dialog").dialog({autoOpen: false});
componentName = ""
do{
    componentName = window.prompt("Name the component", "");
}
while(componentName == "" || componentName == null);
init();
render();

function blinker() {
    $('.blink_me').fadeOut(750);
    $('.blink_me').fadeIn(750);
}

setInterval(blinker, 1500);

function download(filename, text) {
    var element = document.createElement('a');
    element.setAttribute('name', filename);
    element.setAttribute('href', 'data:image/svg,' + encodeURIComponent(text));
    element.setAttribute('download', filename);

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
}
function downloadSVG() {
    var name = componentName + ".dxf"
    getSVGDownload(function(response){
        var data = JSON.parse(response).response;
        download(name, data)
    })

}

function splitComponent()
{
    scene.remove(componentObj);
    delete componentObj;
    componentObj = undefined;
    while(connectedSubcomponents.length > 0){
	scene.add(connectedSubcomponents[connectedSubcomponents.length-1]);
	subcomponents.push(connectedSubcomponents[connectedSubcomponents.length-1]);
	connectedSubcomponents.splice(connectedSubcomponents.length-1,1);
    }
    document.getElementById("sComp").disabled = true;
}


function downloadYaml(){
    var name = componentName + ".yaml"
    getYamlDownload(function(response){
        var data = JSON.parse(response).response;
        download(name, data)
    })
}

function saveComponent(){
    componentSave(componentName, function(){})
}

function fixEdgeInterface(){
    var name, interface, value;
    if(SELECTED != undefined && SELECTED.parent != "Scene") {
        if(SELECTED.parent.type == "MasterComponent") {
            var spl = SELECTED.name.split("_");
		    name = spl[0];
		    interface = spl[1];
        }
        else {
            name = SELECTED.parent.name;
		    interface = SELECTED.name;
        }
        var value = window.prompt("Value to fix interface to");
        fixComponentEdgeInterface(name, interface, value);
    }
}

function downloadModel(){
    if(UrlExists("models/" + componentName + "/graph-model.stl"))
	window.open("models/" + componentName + "/graph-model.stl");
}


function UrlExists(url)
{
    var http = new XMLHttpRequest();
    http.open('HEAD', url, false);
    http.send();
    return http.status!=404;
}

function removeDuplicates(list){
    for(var ele = 0; ele < list.length; ele++){
	for(var ele2 = 0; ele2 < list.length; ele2++){
	    if(ele != ele2 && list[ele].x == list[ele2].x && list[ele].y == list[ele2].y && list[ele].z == list[ele2].z){
		list.splice(ele2,1);
		ele2--;
	    }
	}
    }
}

function createMeshFromObject(obj)
{
    var material = new THREE.MeshPhongMaterial( { color:0xffffff, shading: THREE.FlatShading } );
    var geometry = new THREE.Geometry();
    for(var face in obj["faces"]){
        transf = new THREE.Matrix4();
        //obj["faces"][face][0] = obj["faces"][face][0].map(function(i){return i.replaceAll("**","^").replaceAll("[","(").replaceAll("]",")")})
        transf.elements = obj["faces"][face][0].map(function(i){return evalPrefix(i,obj["solved"]).value});
        transf.transpose();
        console.log(transf);
        var vertices = [];
        set = new Set();
        var holes = [];
        for(var v = 0, len = obj["faces"][face][1]["vertices"].length; v < len; v++){
            try{
            //obj["faces"][face][1]["vertices"][v] = obj["faces"][face][1]["vertices"][v].map(function(i){if(typeof i == 'string' || i instanceof String)return i.replaceAll("**","^").replaceAll("[","(").replaceAll("]",")"); else return i;});
            } catch (err){console.log(face + " " +v);}
            console.log(obj["faces"][face][1]["vertices"][v]);
            var arr = obj["faces"][face][1]["vertices"][v].map(function(i){return evalPrefix(i,obj["solved"]).value});
            console.log(arr);
            set.add(arr[0] + ","+arr[1]);
        }
        if(set.size < 3)
            continue;
        var iter = set.values();
        while(1){
            var element = iter.next();
            if(element["done"] == true)
            break;
            var period = element["value"].indexOf(",");
            vertices.push(new THREE.Vector3(Number(element["value"].substring(0,period)),Number(element["value"].substring(period+1)),0));
        }
        var numverts = geometry.vertices.length;
        var triangles = THREE.Shape.Utils.triangulateShape ( vertices, holes );
        for(var v = 0, len = vertices.length; v < len; v++){
            var vert = new THREE.Vector4(vertices[v].x,vertices[v].y,0,1);
            vert.applyMatrix4(transf);
            vertices[v].x = vert.x; vertices[v].y = vert.y; vertices[v].z = vert.z;
        }
        geometry.vertices = geometry.vertices.concat(vertices);
        for(var t = 0, len = triangles.length; t < len; t++){
            geometry.faces.push(new THREE.Face3(triangles[t][0]+numverts, triangles[t][1]+numverts, triangles[t][2]+numverts));
        }
    }
    var mesh = new THREE.Mesh( geometry, material );
    mesh["solved"] = obj["solved"];
    mesh["faces"] = obj["faces"];
    mesh["edges"] = obj["edges"];
    return mesh;
}

function onComponentSymbolic(obj){
    if(componentObj)
        scene.remove(componentObj);
        //.replaceAll("**","^");
    nupe = obj;
    componentObj = createMeshFromObject(obj);
    componentObj.type = "MasterComponent";
    componentObj.interfaceEdges = obj["interfaceEdges"]
    componentObj.connectedInterfaces = {};
    for(var i = 0, len = connectedSubcomponents.length; i < len; i++) {
        for(var interfaceEdge in connectedSubcomponents[i].interfaceEdges) {
            obj.interfaceEdges[connectedSubcomponents[i].name + "_" + interfaceEdge] = []
            for(var edge = 0, edges = connectedSubcomponents[i].interfaceEdges[interfaceEdge].length; edge < edges; edge++) {
	            obj.interfaceEdges[connectedSubcomponents[i].name + "_" + interfaceEdge].push(connectedSubcomponents[i].name + "_" + connectedSubcomponents[i].interfaceEdges[interfaceEdge][edge]);
	        }
	    }
	}
    for(var i = 0, len = connections.length; i < len; i++) {
        componentObj.connectedInterfaces[connections[i].interface1.replaceAll(".", "_")] = true;
        componentObj.connectedInterfaces[connections[i].interface2.replaceAll(".", "_")] = true;
    }
	highlightInterfaces(componentObj);
    scene.add(componentObj);
}

function loadSymbolic(obj, n){
    nupe = obj;
    var objMesh = createMeshFromObject(obj);

    objMesh.name = n;
    objMesh.className = compName;
    objMesh.interfaces = {};
    objMesh.interfaceEdges = obj["interfaceEdges"];
    objMesh.connectedInterfaces = {};
    objMesh.parameterfuncs = {};
    subcomponents.push(objMesh);
    highlightInterfaces(objMesh);
    comp.subcomponents[objMesh.name] = comp.subcomponents.addFolder(objMesh.name);
    var constrs = comp.subcomponents[objMesh.name].addFolder("Constrain Parameters");
	objMesh.parameters = obj['parameters'];
	for(var pars in objMesh.parameters){
	    var constraintButton = {
	        controller: undefined,
	        c: pars,
		    constrain:function(){
		        var value = window.prompt("Set " + objMesh.name + "_" + this.c + " to: ");
                constrainParameter(objMesh.name, this.c, value);
                this.controller.name(this.c + " = " + value);
		    }
		}
	    var controller = constrs.add(constraintButton, "constrain");
	    constraintButton.controller = controller;
	    controller.name(pars);
	    //if(objMesh.parameters[i] == null)
		//    objMesh.parameters[i] = "";

	    //objMesh.parameterfuncs[i] = "";
	    //f.add(constraintButton, "constrain").name("Constrain");
	    //f.add(objMesh.parameters,i).name("Value");
	    //f.add(objMesh.parameterfuncs,i).name("Function");
	}
    /*var ints = comp.subcomponents[objMesh.name].addFolder("Inherit Interfaces");
    for(var i in componentLibrary[objMesh.className].interfaces){
        var inheritButton = {
            controller: undefined,
            name: objMesh.name,
            interface: componentLibrary[objMesh.className].interfaces[i],
            inherit: function(){
                var intName = window.prompt("Name for inherited interface: ");
                this.controller.name(this.interface + ": Inherited as " + intName);
                inheritInterface(intName, this.name, this.interface);
            }
        }
        var controller = ints.add(inheritButton, "inherit");
        inheritButton.controller = controller;
        controller.name(inheritButton.interface);
	    //objMesh.interfaces[componentLibrary[objMesh.className].interfaces[i]] = false;
    }*/
    scene.add(objMesh);
    /*for(i in objMesh.interfaces){
	    var contr = ints.add(objMesh.interfaces,i)
	    contr.name(i);
    }*/
    var removeButton = {
        delName: objMesh.name,
        remove: function(){
            for(var i = 0, len = subcomponents.length; i < len; i++){
		        if(subcomponents[i].name == this.delName){
		            if(SELECTED != undefined && SELECTED.name == subcomponents[i].name){
			            control.detach(subcomponents[i].name);
			            SELECTED = undefined;
		            }
		            scene.remove(subcomponents[i]);
		            subcomponents.splice(i,1);
		            break;
		        }
	        }
	        removeByName(connectedSubcomponents,this.delName);
	        comp.subcomponents.removeFolder(this.delName);
	        for(var i = 0, len = connections.length; i < len; i++){
	            if(connections[i].interface1.substr(0,connections[i].interface1.indexOf(".")) == this.delName)
	            {
	                var otherName = connections[i].interface2.substr(0,connections[i].interface2.indexOf("."));
	                console.log(otherName);
	                for(var j = 0, slen = subcomponents.length; j < slen; j++){
	                    if(subcomponents[j].name == otherName)
	                        delete subcomponents[j].connectedInterfaces[connections[i].interface2.substr(connections[i].interface2.indexOf(".")+1)];
	                }
	                for(var j = 0, slen = connectedSubcomponents.length; j < slen; j++){
	                    if(connectedSubcomponents[j].name == otherName)
	                        delete connectedSubcomponents[j].connectedInterfaces[connections[i].interface1.substr(connections[i].interface1.indexOf(".")+1)];
	                }
	                comp.connections.removeFolder(connections[i].name);
	                connections.splice(i, 1);
	                i--;
	                len--;
                }
                else if(connections[i].interface2.substr(0,connections[i].interface2.indexOf(".")) == this.delName)
                {
                    var otherName = connections[i].interface1.substr(0,connections[i].interface1.indexOf("."));
                    console.log(otherName);
	                for(var j = 0, slen = subcomponents.length; j < slen; j++){
	                    if(subcomponents[j].name == otherName)
	                        delete subcomponents[j].connectedInterfaces[connections[i].interface1.substr(connections[i].interface1.indexOf(".")+1)];
	                }
	                for(var j = 0, slen = connectedSubcomponents.length; j < slen; j++){
	                    if(connectedSubcomponents[j].name == otherName)
	                        delete connectedSubcomponents[j].connectedInterfaces[connections[i].interface1.substr(connections[i].interface1.indexOf(".")+1)];
	                }
	                comp.connections.removeFolder(connections[i].name);
	                connections.splice(i, 1);
	                i--;
	                len--;
                }
	        }
	        console.log("deleting: " + this.delName);
	        var over = '<div id="overlay">' +
                    '<span class="blink_me">LOADING...</span>' +
                    '</div>';
            $(over).appendTo('body');
	        delSubcomponent(this.delName, function(response){$('#overlay').remove();});
        }
    }
    comp.subcomponents[objMesh.name].add(removeButton, "remove").name("Delete");
}

function highlightInterfaces(objMesh)
{
    for(i in objMesh.interfaceEdges){
	if(objMesh.connectedInterfaces[i] == undefined){
	    for(var j = 0, len =objMesh.interfaceEdges[i].length; j < len; j++){
		if(objMesh.interfaceEdges[i][j] == null)
		    continue;
		var material = new THREE.LineBasicMaterial({
			color: 0xff0000
		    });
		var geometry = new THREE.Geometry();
		var k = objMesh.interfaceEdges[i][j];
		var p1 = [], p2 = [];
		for(var p = 0; p < 2; p++){
		    for(var c = 0; c < 3; c++){
			//objMesh["edges"][k][p][c] = objMesh["edges"][k][p][c]
			//objMesh["edges"][k][p][c] = objMesh["edges"][k][p][c].replaceAll("**","^").replaceAll("[", "(").replaceAll("]", ")");
			//.replaceAll("**","^");
			if(p == 0)
			    p1.push(evalPrefix(objMesh["edges"][k][p][c],objMesh["solved"]).value);
			else
			    p2.push(evalPrefix(objMesh["edges"][k][p][c],objMesh["solved"]).value);
		    }
		}
		geometry.vertices.push(
				       new THREE.Vector3( p1[0], p1[1], p1[2] ),
				       new THREE.Vector3( p2[0], p2[1], p2[2] )
				       );
		var line = new THREE.Line( geometry, material );
		line.name = i;
		objMesh.add(line);
	    }
	}
    }

}

function onLoadSTL(geometry){
    var n = window.prompt("Subcomponent Name","");
    if(n == "" || n == null)
	return;
    var joined = subcomponents.concat(connectedSubcomponents);
    for(var iter = 0,len=joined.length; iter < len; iter++){
	if(joined[iter].name == n){
	    window.alert('Subcomponent with name "' + n + '" already exists');
	    return;
	}
    }
    var material = new THREE.MeshPhongMaterial( { color:0xffffff, shading: THREE.FlatShading } );
    var obj = new THREE.Mesh(geometry,material);
    obj.name = n;
    obj.className = compName;
    obj.interfaces = {};
    obj.interfaceEdges = interfaceEdges;
    obj.parameterfuncs = {};
    subcomponents.push(obj);
    for(i in obj.interfaceEdges){
	for(j in interfaceEdges[i]){
	    if(interfaceEdges[i][j] == null)
		continue;
	    var material = new THREE.LineBasicMaterial({
		    color: 0xff0000
		});
	    var geometry = new THREE.Geometry();
	    geometry.vertices.push(
				   new THREE.Vector3( interfaceEdges[i][j][0][0], interfaceEdges[i][j][0][1], interfaceEdges[i][j][0][2] ),
				   new THREE.Vector3( interfaceEdges[i][j][1][0], interfaceEdges[i][j][1][1], interfaceEdges[i][j][1][2] )
				   );
	    var line = new THREE.Line( geometry, material );
	    line.name = i;
	    obj.add(line);
	}
    }
    comp.subcomponents[obj.name] = comp.subcomponents.addFolder(obj.name);
    var constrs = comp.subcomponents[obj.name].addFolder("Constraints");
    /*picoModule.getParameters(compName,function(response){
	obj.parameters = response;
	for(i in obj.parameters){
	    var f = constrs.addFolder(i);
	    if(obj.parameters[i] == null)
		obj.parameters[i] = "";
	    obj.parameterfuncs[i] = "";
	    f.add(obj.parameters,i).name("Value");
	    f.add(obj.parameterfuncs,i).name("Function");
	}
    });*/
    for(i in componentLibrary[obj.className].interfaces){
	obj.interfaces[componentLibrary[obj.className].interfaces[i]] = false;
    }
    scene.add(obj);
    var ints = comp.subcomponents[obj.name].addFolder("Inherit Interfaces");
    for(i in obj.interfaces){
	var contr = ints.add(obj.interfaces,i)
	contr.name(i);
    }
}

function onComponentSTL(geometry){
    if(componentObj)
	scene.remove(componentObj);
    material = new THREE.MeshPhongMaterial( {color:0xffffff,shading:THREE.FlatShading});
    componentObj = new THREE.Mesh(geometry,material);
    scene.add(componentObj);
}

function handleError(e){
    var ind = e.exception.search("Parameter ");
    if(ind != -1){
	var param = [];
	if(e.exception.charAt(ind+10) == '[')
	    param = eval(e.exception.substring(ind+10,e.exception.search(']')+1))
	else{
	    var strip = e.exception.substring(ind+10);
	    param.push(strip.substring(0,strip.search(' ')));
	}
	for(var i = 0, len = param.length; i < len; i++){
	    var val = window.prompt("Set value for parameter " + param[i]);
	    if(val == "" || val == null)
		return;
	    tempParams[param[i]] = parseInt(val);
	}
	var args = [compName,tempParams];
	/*picoModule.generate_stl(args, function(response){
	    tempParams = {};
	    console.log(response);
	    interfaceEdges = response;
	    stl_loader.load('models/' + compName + '/graph-model.stl',onLoadSTL);
	});*/
    }
    else
	window.alert(e.exception);
}

function getComponents()
{
	//for(var key in componentMenus){
	    getComponentList("" ,function(response){
	    response = JSON.parse(response).response;
		for(i = 0; i < response.length; i++){
		    componentLibrary[response[i][0]] = { interfaces: response[i][1] };
		    var button = {
			compName: response[i][0],
			add: function(){
			    compName = this.compName;
			    var args = [this.compName,tempParams];
			    componentCount++;
			    var n = window.prompt("Subcomponent Name","");
                if(n == "" || n == null)
	                return;
                var joined = subcomponents.concat(connectedSubcomponents);
                for(var iter = 0,len=joined.length; iter < len; iter++){
	            if(joined[iter].name == n){
	                window.alert('Subcomponent with name "' + n + '" already exists');
	                return;
	            }
                }
                var over = '<div id="overlay">' +
                    '<span class="blink_me">LOADING...</span>' +
                    '</div>';
                $(over).appendTo('body');
			    addSubcomponent(n,compName, function(response){
			    response = JSON.parse(response).response;
				tempParams = {};
				loadSymbolic(response,n);
				/*interfaceEdges = response;
				  stl_loader.load('models/' + compName + '/graph-model.stl',onLoadSTL);*/
				  $('#overlay').remove();
			    });
			}
		    }
		    componentsFolder.add(button,"add").name(response[i][0]);
		}
	    });
	//}

}

function init(){
    container = document.getElementById('componentView');
    svgcontainer = document.getElementById('svg-view');

    scene = new THREE.Scene();
    svgscene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera( 75, container.clientWidth / container.clientHeight, 0.1, 100000 );
    //camera = new THREE.OrthographicCamera(container.offsetWidth / -2, container.offsetWidth / 2, container.offsetHeight / 2, container.offsetHeight / -2, 0.1, 100000);
    svgcamera = new THREE.OrthographicCamera(svgcontainer.offsetWidth / -2, svgcontainer.offsetWidth / 2, svgcontainer.offsetHeight / 2, svgcontainer.offsetHeight / -2, 1, 1000);

    stl_loader = new THREE.STLLoader();
    renderer = new THREE.WebGLRenderer({alpha: true, antialias: true});
    renderer.setSize( container.clientWidth, container.clientHeight);
    renderer.setClearColor( 0x000000,0);
    svgrenderer = new THREE.WebGLRenderer({alpha:true,antialias: true});
    svgrenderer.setSize(svgcontainer.clientWidth,svgcontainer.clientHeight);
    svgrenderer.setClearColor(0x000000,0);
    container.appendChild( renderer.domElement );
    svgcontainer.appendChild(svgrenderer.domElement);
    scene.add( new THREE.GridHelper( 500, 100 ) );
    camera.position.set( 1000, 500, 1000 );
    camera.lookAt( new THREE.Vector3( 0, 200, 0 ) );
    svgcamera.position.set(0,1000,0);
    svgcamera.lookAt(new THREE.Vector3(0,0,0));
    light = new THREE.DirectionalLight( 0xffffff );
    light.position.set( 1, 1, 1 );
    scene.add( light );

    light = new THREE.DirectionalLight( 0x002288 );
    light.position.set( -1, -1, -1 );
    scene.add( light );

    light = new THREE.AmbientLight( 0x222222 );
    scene.add( light );
    control = new THREE.TransformControls( camera, renderer.domElement );
    control.addEventListener( 'change', render );
    orbit = new THREE.OrbitControls( camera, renderer.domElement );
    loadGui();
    getComponents();
    createComponent();
    renderer.domElement.addEventListener( 'mousemove', onDocumentMouseMove, false );
    renderer.domElement.addEventListener( 'mousedown', onDocumentMouseDown, false );
    renderer.domElement.addEventListener( 'mouseup', onDocumentMouseUp, false );

    window.addEventListener( 'resize', onWindowResize, false );
    window.addEventListener( 'keydown', onKeyDown);
}

function removeByName(array,name){
    for(var i = 0, len = array.length; i < len; i++){
	if(array[i].name == name){
	    array.splice(i,1);
	    break;
	}
    }
}

function loadGui() {
    var search = {
	Search: ""
    };
    var filters = {
	Mechanical: true,
	Electrical: true,
	Software: true
    };
    gui = new dat.GUI({ autoPlace: false, width: document.getElementById('left-panel').clientWidth, scrollable: true });
    gui.domElement.removeChild(gui.__closeButton);
    document.getElementById('left-panel').appendChild(gui.domElement);
    gui.add(search, "Search");
    searchFilters = gui.addFolder("Filters");
    searchFilters.add(filters, "Mechanical");
    searchFilters.add(filters, "Electrical");
    searchFilters.add(filters, "Software");
    componentsFolder = gui.addFolder('Components');
    componentsFolder.open();
    //componentMenus["mechanical"] = componentsFolder.addFolder("Mechanical");
    //componentMenus["device"] = componentsFolder.addFolder("Device");
    //componentMenus["actuator"] = componentsFolder.addFolder("Actuators");
    //componentMenus["sensor"] = componentsFolder.addFolder("Sensors");
    //componentMenus["UI"] = componentsFolder.addFolder("UI");
    rightpanel = new dat.GUI({ autoPlace: false, width: document.getElementById('right-panel').clientWidth, scrollable: true });
    rightpanel.domElement.removeChild(rightpanel.__closeButton);
    document.getElementById('right-panel').appendChild(rightpanel.domElement);
    comp = rightpanel.addFolder(componentName);
    comp.open();
    comp.parameters = comp.addFolder("Parameters");
    comp.interfaces = comp.addFolder("Interfaces");
    comp.subcomponents = comp.addFolder("Subcomponents");
    comp.connections = comp.addFolder("Connections");
    var objectbuttons = {
	subcomponentDelete:function(){
	    var delName = window.prompt("Name of subcomponent to delete","");
	    if(delName == "" || delName == null)
		return;
	    for(var i = 0, len = subcomponents.length; i < len; i++){
		if(subcomponents[i].name == delName){
		    if(SELECTED.name == subcomponents[i].name){
			control.detach(subcomponents[i].name);
			SELECTED = undefined;
		    }
		    scene.remove(subcomponents[i]);
		    subcomponents.splice(i,1);
		    break;
		}
	    }
	    removeByName(connectedSubcomponents,delName);
	    comp.subcomponents.removeFolder(delName);
	},
	connectionAdd:function(){
	    if(SELECTED != undefined && SELECTED_2 != undefined && SELECTED.parent != "Scene" && SELECTED_2.parent != "Scene")
	    {
		var newConn = {};
		newConn.name = window.prompt("Connection Name: ");
		if(newConn.name == "" || newConn.name == null)
		    return;
		for(var iter = 0, len = connections.length; iter < len; iter++){
		    if(connections[iter].name == newConn.name){
			window.alert('Connection with name "' + newConn.name + '" already exists');
			return;
		    }
		}
		angle = window.prompt("Connection Angle: ");
		if(angle == "" || angle == null || isNaN(angle))
            return;
		if(SELECTED.parent.type == "MasterComponent"){
		    newConn.interface1 = SELECTED.name.replaceAll("_", ".");
		    var spl = SELECTED.name.split("_");
		    s1pname = spl[0];
		    s1name = spl[1];
		}
		else {
		    newConn.interface1 = SELECTED.parent.name + "." + SELECTED.name;
		    s1pname = SELECTED.parent.name;
		    s1name = SELECTED.name;
		}
		if(SELECTED_2.parent.type == "MasterComponent") {
		    newConn.interface2 = SELECTED_2.name.replaceAll("_", ".");
		    var spl = SELECTED_2.name.split("_");
		    s2pname = spl[0];
		    s2name = spl[1];
		}
		else {
		    newConn.interface2 = SELECTED_2.parent.name + "." + SELECTED_2.name;
		    s2pname = SELECTED_2.parent.name;
		    s2name = SELECTED_2.name;
		}
		var over = '<div id="overlay">' +
                    '<span class="blink_me">LOADING...</span>' +
                    '</div>';
            $(over).appendTo('body');
		addComponentConnection(s1pname,s1name,s2pname,s2name, angle, function(){$('#overlay').remove();});//function(){buildComponent()});
		connections.push(newConn);
		SELECTED.parent.connectedInterfaces[SELECTED.name] = newConn.interface2;
		SELECTED_2.parent.connectedInterfaces[SELECTED_2.name] = newConn.interface1;
		var folder = comp.connections.addFolder(newConn.name);
		newConn.args = "";
		var connFixButton = {
		    s1pname: s1pname,
		    s1name: s1name,
		    fixConnection:function(){
		        var value = window.prompt("Value to fix interface to");
                fixComponentEdgeInterface(this.s1pname, this.s1name, value);
		    }
		}
		folder.add(newConn,"interface2").name(newConn.interface1);
		folder.add(connFixButton, "fixConnection").name("Set Length");
	    }
	    /*else{
		var joinedList = subcomponents.concat(connectedSubcomponents);
		for(i in joinedList){
		    for(inter in joinedList[i].interfaces){
			var opt = document.createElement("option");
			var opt2 = document.createElement("option");
			var str = joinedList[i].name + "." + inter;
			opt.val = str; opt2.val = str;
			opt.innerHTML = str; opt2.innerHTML = str;
			document.getElementById('interface1').appendChild(opt);
			document.getElementById('interface2').appendChild(opt2);
		    }
		}
		$("#dialog").dialog("open");
	    }*/
	},
	connectionAddTab:function(){
	    if(SELECTED != undefined && SELECTED_2 != undefined && SELECTED.parent != "Scene" && SELECTED_2.parent != "Scene")
	    {
		var newConn = {};
		newConn.name = window.prompt("Connection Name: ");
		if(newConn.name == "" || newConn.name == null)
		    return;
		for(var iter = 0, len = connections.length; iter < len; iter++){
		    if(connections[iter].name == newConn.name){
			window.alert('Connection with name "' + newConn.name + '" already exists');
			return;
		    }
		}
		angle = window.prompt("Connection Angle: ");
		if(angle == "" || angle == null || isNaN(angle))
            return;
		if(SELECTED.parent.type == "MasterComponent"){
		    newConn.interface1 = SELECTED.name.replaceAll("_", ".");
		    var spl = SELECTED.name.split("_");
		    s1pname = spl[0];
		    s1name = spl[1];
		}
		else {
		    newConn.interface1 = SELECTED.parent.name + "." + SELECTED.name;
		    s1pname = SELECTED.parent.name;
		    s1name = SELECTED.name;
		}
		if(SELECTED_2.parent.type == "MasterComponent") {
		    newConn.interface2 = SELECTED_2.name.replaceAll("_", ".");
		    var spl = SELECTED_2.name.split("_");
		    s2pname = spl[0];
		    s2name = spl[1];
		}
		else {
		    newConn.interface2 = SELECTED_2.parent.name + "." + SELECTED_2.name;
		    s2pname = SELECTED_2.parent.name;
		    s2name = SELECTED_2.name;
		}
		addTabConnection(s1pname,s1name,s2pname,s2name, angle, function(){});//function(){buildComponent()});
		connections.push(newConn);
		SELECTED.parent.connectedInterfaces[SELECTED.name] = newConn.interface2;
		SELECTED_2.parent.connectedInterfaces[SELECTED_2.name] = newConn.interface1;
		var folder = comp.connections.addFolder(newConn.name);
		newConn.args = "";
		var connFixButton = {
		    s1pname: s1pname,
		    s1name: s1name,
		    fixConnection:function(){
		        var value = window.prompt("Value to fix interface to");
                fixComponentEdgeInterface(this.s1pname, this.s1name, value);
		    }
		}
		folder.add(newConn,"interface2").name(newConn.interface1);
		folder.add(connFixButton, "fixConnection").name("Set Length");
	    }
	    /*else{
		var joinedList = subcomponents.concat(connectedSubcomponents);
		for(i in joinedList){
		    for(inter in joinedList[i].interfaces){
			var opt = document.createElement("option");
			var opt2 = document.createElement("option");
			var str = joinedList[i].name + "." + inter;
			opt.val = str; opt2.val = str;
			opt.innerHTML = str; opt2.innerHTML = str;
			document.getElementById('interface1').appendChild(opt);
			document.getElementById('interface2').appendChild(opt2);
		    }
		}
		$("#dialog").dialog("open");
	    }*/
	},
	connectionDelete:function(){
	    var delName = window.prompt("Name of connection to delete","");
	    if(delName == "" || delName == null)
		return;
	    removeByName(connections,delName);
	    comp.connections.removeFolder(delName);
	},
	parameterAdd:function(){
	    var fieldName = window.prompt("Parameter name","");
	    if(fieldName == "" || fieldName == null)
		return;
	    if(parameters[fieldName] != undefined){
		window.alert('Parameter "' + fieldName + '" already exists');
		return;
	    }
	    var pdef = window.prompt("Default value: ");
	    if(pdef == "" || pdef == null || isNaN(pdef))
	        return;
	    parameters[fieldName] = pdef;
	    comp.parameters.add(parameters, fieldName).name(fieldName);
	    addParameter(fieldName, pdef);
	},
	parameterDelete:function(){
	    var delName = window.prompt("Name of parameter to delete","");
	    if(delName == "" || delName == null)
		return;
	    delete parameters[delName];
	    for(var i = 2, len = comp.parameters.__controllers.length; i < len; i++){
		if(comp.parameters.__controllers[i].__li.firstElementChild.firstElementChild.innerHTML == delName)
		    comp.parameters.remove(comp.parameters.__controllers[i]);
	    }
	    delParameter(delName);
	},
	interfaceAdd:function(){
	    if(SELECTED != undefined && SELECTED.parent != "Scene")
	    {
	        var name = window.prompt("Name for inherited interface: ");
	        if(name == "" || name == null)
	            return;
            if(SELECTED.parent.type == "MasterComponent"){
                var spl = SELECTED.name.split("_");
                s1pname = spl[0];
                s1name = spl[1];
            }
            else {
                s1pname = SELECTED.parent.name;
                s1name = SELECTED.name;
            }
            interfaces[name] = s1pname + "." + s1name;
            comp.interfaces.add(interfaces, name).name(name);
            inheritInterface(name, s1pname, s1name);
		}
	},
	interfaceDelete:function(){
	    var delName = window.prompt("Name of interface to delete","");
	    if(delName == "" || delName == null)
		return;
		delete interfaces[delName];
		for(var i = 2, len = comp.interfaces.__controllers.length; i < len; i++){
		if(comp.interfaces.__controllers[i].__li.firstElementChild.firstElementChild.innerHTML == delName)
		    comp.interfaces.remove(comp.interfaces.__controllers[i]);
	    }
	    delInterface(delName);
	}
    }
    //comp.subcomponents.add(objectbuttons,'subcomponentDelete').name("Remove");
    comp.parameters.add(objectbuttons,'parameterAdd').name("Add");
    comp.parameters.add(objectbuttons,'parameterDelete').name("Delete");
    comp.connections.add(objectbuttons,'connectionAdd').name("Add");
    comp.connections.add(objectbuttons,'connectionAddTab').name("Add Tab");
    comp.interfaces.add(objectbuttons, 'interfaceAdd').name("Add");
    comp.interfaces.add(objectbuttons, 'interfaceDelete').name("Delete");
    //comp.connections.add(objectbuttons,'connectionDelete').name("Remove");
}

function stripObjects(list, strippedList){
    for(i in list){
	var strippedObj = {};
	strippedObj.name = list[i].name;
	strippedObj.className = list[i].className;
	strippedObj.parameters = list[i].parameters;
	strippedObj.parameterfuncs = list[i].parameterfuncs;
	strippedObj.interfaces = list[i].interfaces;
	strippedList.push(strippedObj);
    }
}

function updateComponent(component, response)
{
    solution = response["solved"]
    var pos = {};
    var quat = {};
    for(var k in component["solved"]){
	if(k == "dx" || k == "dy" || k == "dz"){
	    pos[k] = solution[component.name + "_" + k];
	    component["solved"][k] = 0;
	}
	else if(k == "q_a" || k == "q_i" || k == "q_j" || k == "q_k"){
	    quat[k] = solution[component.name + "_" + k];
	    if(k == "q_a")
		component["solved"][k] = 1;
	    else
		component["solved"][k] = 0;
	}
	else
	    component["solved"][k] = solution[component.name + "_" + k];
    }
    component['faces'] = {}
    for(var face in response['faces']){
        if (face.startsWith(component.name))
            component['faces'][face] = response['faces'][face];
    }
    /*component['edges'] = {}
    for(var edge in response['edges']){
        if (edge.startsWith(component.name))
            component['edges'][edge] = response['edges'][edge];
    }*/
    console.log(pos);
    console.log(quat);
    newComp = createMeshFromObject(component);
    newComp.position.set(Number(pos.dx),Number(pos.dy),Number(pos.dz));
    newComp.rotation.setFromQuaternion(new THREE.Quaternion(Number(quat.q_i),Number(quat.q_j),Number(quat.q_k),Number(quat.q_a)));
    newComp.name = component.name;
    newComp.className = component.className;
    newComp.interfaces = component.interfaces;
    newComp.interfaceEdges = component.interfaceEdges;
    newComp.connectedInterfaces = component.connectedInterfaces;
    newComp.parameterfuncs = component.parameterFuncs;
    highlightInterfaces(newComp);
    return newComp;
}
function build(){

    buildComponent();


}
function buildComponent(){
    var over = '<div id="overlay">' +
            '<span class="blink_me">LOADING...</span>' +
            '</div>';
    $(over).appendTo('body');
    var thisComponent = {};
    thisComponent.name = componentName;
    thisComponent.subcomponents = [];
    stripObjects(subcomponents,thisComponent.subcomponents);
    stripObjects(connectedSubcomponents,thisComponent.subcomponents);
    thisComponent.parameters = parameters;
    thisComponent.connections = connections;
    makeComponent(function(response){
        response = JSON.parse(response).response;
	    if(SELECTED != undefined){
	        control.detach(SELECTED);
	        SELECTED = undefined;
	    }
	    for(var i = 0, len = connectedSubcomponents.length;i < len; i++)
	        connectedSubcomponents[i] = updateComponent(connectedSubcomponents[i],response);
	    while(subcomponents.length > 0){
	        scene.remove(subcomponents[subcomponents.length-1]);
	        subcomponents[subcomponents.length-1] = updateComponent(subcomponents[subcomponents.length-1],response);
	        connectedSubcomponents.push(subcomponents[subcomponents.length-1]);
	        subcomponents.splice(subcomponents.length-1,1);
	    }
	    onComponentSymbolic(response);
	//	stl_loader.load('models/' + componentName + '/graph-model.stl',onComponentSTL);
	//	document.getElementById('svg-view').src = 'models/' + componentName + '/graph-print.svg';

	    document.getElementById('sComp').disabled = false;
	    //document.getElementById('dModel').disabled = false;
	    //document.getElementById('sComp').disabled = false;
	    $('#overlay').remove();
	    viewSVG();
    });
}

function onKeyDown( event ) {
    switch ( event.keyCode ) {
	/*    case 81: // Q
	      control.setSpace( control.space === "local" ? "world" : "local" );
	      break;
    case 17: // Ctrl
    control.setTranslationSnap( 100 );
    control.setRotationSnap( THREE.Math.degToRad( 15 ) );
    break;*/
    case 87: // W
    control.setMode( "translate" );
    break;
    case 69: // E
    control.setMode( "rotate" );
    break;
    case 82: // R
    control.setMode( "scale" );
    break;
    /*    case 187:
    case 107: // +, =, num+
    control.setSize( control.size + 0.1 );
    break;
    case 189:
    case 109: // -, _, num-
    control.setSize( Math.max( control.size - 0.1, 0.1 ) );
    break;
    case 66: // B
    buildComponent();
    break;*/
    }
}

function onWindowResize() {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize( container.clientWidth, container.clientHeight );
    document.getElementById('left-panel').style.height = window.innerHeight;
}

function getLeftPos(el) {
    for (var leftPos = 0;
	 el != null;
	 leftPos += el.offsetLeft, el = el.offsetParent);
    return leftPos;
}

function onDocumentMouseMove( event ) {
    event.preventDefault();
    mouse.x = ( (event.clientX - getLeftPos(container))/ container.clientWidth ) * 2 - 1;
    mouse.y = - ( event.clientY / container.clientHeight ) * 2 + 1;
    raycaster.setFromCamera( mouse, camera );
    var objs = subcomponents;
    if(componentObj != undefined)
	objs = subcomponents.concat(componentObj);
    var intersects = raycaster.intersectObjects( objs,true );
    if ( intersects.length > 0 ) {
	container.style.cursor = 'pointer';
    } else {
	container.style.cursor = 'auto';
    }
}

function onDocumentMouseDown( event ) {
    event.preventDefault();
    raycaster.setFromCamera( mouse, camera );
    var objs = subcomponents;
    if(componentObj != undefined)
	objs = subcomponents.concat(componentObj);
    var intersects = raycaster.intersectObjects( objs,true );
    var obj;
    if(!event.shiftKey)
	obj = SELECTED;
    else
	obj = SELECTED_2;
    if ( intersects.length > 0 ) {
	if(obj != undefined && obj.parent.type != "Scene")
	{
	    obj.material.color = new THREE.Color(0xff0000);
	    if(!event.shiftKey)
		SELECTED = undefined;
	    else
		SELECTED_2 = undefined;
	}
	/*if(intersects[0].object.parent.type == "MasterComponent")
	    {
		if(!event.shiftKey)
		    {
			SELECTED = intersects[0].object.parent;
			control.attach(SELECTED);
		    }
	    }*/
	if(intersects[0].object.parent.type != "Scene"){
	    intersects[0].object.material.color = new THREE.Color(0x00ff00);
	    if(!event.shiftKey){
		if(SELECTED != undefined && SELECTED.parent.type == "Scene")
		    control.detach(SELECTED);
		SELECTED = intersects[0].object;
	    }
	    else
		SELECTED_2 = intersects[0].object;
	}
	else
	{
	    control.attach(intersects[0].object);
	    scene.add(control);
	    comp.subcomponents.open();
	    if(SELECTED != undefined && SELECTED != componentObj)
		    comp.subcomponents[SELECTED.name].close();
	    SELECTED = intersects[0].object;
	    if(SELECTED != componentObj)
		    comp.subcomponents[intersects[0].object.name].open();
	}
    }
}

function onDocumentMouseUp( event ) {
    event.preventDefault();
}

function render() {
    requestAnimationFrame(render);
    control.update();
    renderer.render( scene, camera );
}

function viewSVG(){
    var over = '<div id="overlay">' +
                    '<span class="blink_me">LOADING...</span>' +
                    '</div>';
    $(over).appendTo('body');
    var drawing_div = document.getElementById('svg-view');
     getSVG(function(response){
        response = JSON.parse(response).response;
        drawing_div.style.backgroundColor = 'white'
        //drawing_div.style.padding = "2%";
        drawing_div.innerHTML = response;
        document.getElementById('dSVG').disabled = false;
        $('#overlay').remove();
      });
}

dat.GUI.prototype.removeFolder = function(name) {
    var folder = this.__folders[name];
    if (!folder) {
	return;
    }
    folder.close();
    this.__ul.removeChild(folder.domElement.parentNode);
    delete this.__folders[name];
    this.onResize();
}

String.prototype.replaceAll = function(search, replacement) {
    var target = this;
    return target.split(search).join(replacement);
};