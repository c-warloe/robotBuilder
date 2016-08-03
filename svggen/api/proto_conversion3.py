import svggen.utils.mymath as math
from svggen.utils.mymath import Abs, Id
import sys
import IPython

from svggen.api import proto as proto_symbolic
from svggen.api.proto import template_pb2 as proto_template

class proto:
  symbolic = proto_symbolic
  template = proto_template
  
template_num = 1
control_num = 0
face_name_to_id = {}
id_to_face = {}
param_to_id = {}
name_to_edge_id = {}
drawing_edge_to_my_edges = {}
drawing_edge_to_faces = {}
drawing_edge_to_vertices = {}
drawing_edge_is_tab = {}
my_edge_to_template = {}
same_variable = {}
tolerance = 1e-10

GLOBALX_3D = "globalx_3d"
GLOBALY_3D = "globaly_3d"
GLOBALZ_3D = "globalz_3d"
GLOBALX_2D = "globalx_2d"
GLOBALY_2D = "globaly_2d"


global graph
graph = None
assumptions = None

def _simplify(exp):
    #IPython.embed()
    
    exp = math.nsimplify(exp).replace(Abs, Id) #TODO: use assumptions
    exp = math.nsimplify(math.simplify(math.refine( math.nsimplify(math.N(exp, tolerance)), assumptions)))
   
    return exp

def append_to_dict(dictionary, key, value):
    if not key in dictionary:
        dictionary[key] = [value]
    else:
        dictionary[key].append(value)
        
def populate_parameter(name, default, template):
    if name not in param_to_id: #If it's already there don't re-add it.
        parameter = template.parameter.add()
        param_id = len(param_to_id) #TODO: populate this dictionary
        parameter.id = param_id
        parameter.name = name
        parameter.default = default
        param_to_id[name] = param_id

def populate_edge(edge, name, idx1, idx2, drawing_edge, template):
    edge_id = len(name_to_edge_id)
    edge.id = edge_id
    edge.name = name
    edge.vertex1_id = idx1
    edge.vertex2_id = idx2
    name_to_edge_id[name] = edge_id

    #And now some book-keeping for later
    append_to_dict( drawing_edge_to_my_edges, drawing_edge.name, edge_id )
    append_to_dict( drawing_edge_to_vertices, drawing_edge.name, (idx1, idx2) )


    #Both should have the same data in this case, since you need two sides to a tab.
    drawing_edge_is_tab[drawing_edge.name] = drawing_edge.isTab

    my_edge_to_template[edge_id] = template
    
    
def constrain_params(param1, param2, parent_template):
    #IPython.embed()
    p1 = param_to_id[param1]
    p2 = param_to_id[param2]
    new_constraint = parent_template.feasible_set.constraint_list.constraint.add()
    new_constraint.linear_constraint.expr.parameter_id.append( p1 )
    new_constraint.linear_constraint.expr.coeff.append( 1.0 )
    new_constraint.linear_constraint.expr.parameter_id.append( p2 )
    new_constraint.linear_constraint.expr.coeff.append( -1.0 )
    new_constraint.linear_constraint.type = 1
    
    
def populateSide(component, template, new_constraint, coeffs, negative): #TODO: modularize this and the append_vertex methods...
    if negative:
        mult = -1
    else:
        mult = 1

    d = new_constraint.linear_constraint.expr
    for key in coeffs:
        try:
            k = float(_simplify(key))
            d.const += mult * float(coeffs[key])
            
        except Exception:  #TODO: make cast exception
            #IPython.embed()
            print key
            try:
                default = component.defaults[key.name] #get the default value
            except Exception:
                print 'populate side exception'
                IPython.embed()
            #print key
            param_name = template.name + '.' + key.name
            populate_parameter(param_name, default, template)
            append_to_dict(same_variable, key.name, param_name)
            d.parameter_id.append(param_to_id[param_name])
            d.coeff.append(mult * float(_simplify(coeffs[key])))
    
    
def addConstraint(component, constraint, parent):

    new_constraint = parent.feasible_set.constraint_list.constraint.add()
    
    lhs = constraint[0]
    op = constraint[1]
    rhs = constraint[2]
    
    if op == "<":
        new_constraint.linear_constraint.type = 2
        
        #Add assumption
        #TODO: can I do this for equality as well?

        expr = math.sympify(lhs) - math.sympify(rhs)


        global assumptions
        if assumptions is None:
            assumptions = math.Q.positive(expr)
        else:
            assumptions = assumptions & math.Q.positive(expr)
        
        
    elif op == "==":
        new_constraint.linear_constraint.type = 1
    else:
        raise Exception("Not a valid operator type: please specify == or <")
        
    lhscoeffs = _simplify(lhs).as_coefficients_dict()
    rhscoeffs = _simplify(rhs).as_coefficients_dict()
    populateSide(component, parent, new_constraint, lhscoeffs, False)
    populateSide(component, parent, new_constraint, rhscoeffs, True)
    
    
    
    
def addConstraints(component, parent):
    for constraint in component.semanticConstraints:
        addConstraint(component, constraint, parent)
    
def append_vertex(d, component, exp, template, global_param=None):
    print exp
    #coeffs = math.simplify(math.nsimplify(math.simplify(math.N(exp)), tolerance=1e-5)).as_coefficients_dict()
    coeffs = _simplify(exp).as_coefficients_dict()
    
    if global_param is not None:
        param_name = template.name + "." + global_param
        populate_parameter(param_name, 0.0, template)
        append_to_dict(same_variable, global_param, param_name)
        d.parameter_id.append(param_to_id[param_name])
        d.coeff.append(1.0)
    
    for key in coeffs:
        try:
            k = float(_simplify(key))
            d.const += float(coeffs[key])
            
        except Exception:  #TODO: make cast exception
            #IPython.embed()
            print key
            try:
                default = component.defaults[key.name] #get the default value
            except Exception:
                IPython.embed()
            #print key
            param_name = template.name + '.' + key.name
            populate_parameter(param_name, default, template)
            append_to_dict(same_variable, key.name, param_name)
            d.parameter_id.append(param_to_id[param_name])
            d.coeff.append(float(_simplify(coeffs[key])))
            
def parameterize(component, template):
    for parameter in component.parameters:
        populate_parameter(parameter, component.defaults[parameter], template)
        #populate_parameter(parameter, component.defaults[parameter], template)
            

def populate_face(component, face, template, parent):

    #TODO: remove this eventually, not needed.
    #populate_parameter(face.name + ".x", 0.0, template.parameter.add())
    #populate_parameter(face.name + ".y", 0.0, template.parameter.add())
    #populate_parameter(face.name + ".z", 0.0, template.parameter.add())

    #2D SECTION
    #Next, we add 2D vertices as functions of these parameters
    vert_idx = 0

    #Vertices
    num_skipped = 0

    template.name = face.name
    
    #math.simplify(math.nsimplify(math.simplify(math.N(math.transpose(face.get3DCoords()))), 1e-5))
    try:
        #coords2D = math.nsimplify(math.N(math.simplify(math.transpose(face.get2DCoords()))), tolerance=1e-5)
        #coords2D = math.simplify(math.N(math.nsimplify(math.simplify(math.transpose(face.get2DCoords())), 1e-5)))
        coords2D = math.simplify(math.transpose(face.get2DCoords()))
        print '2d coords are'
        print coords2D
    except Exception:
        #coords2D = math.simplify(math.N(math.nsimplify(math.N(math.transpose(face.get2DCoords())), tolerance=1e-5)))
        print '2d exception'
        
        #assume it's constants, which is bad for C++, but oh well
        IPython.embed()
        coords2D = math.transpose(face.get2DCoords())
        
        #IPython.embed()

    for j in range(math.rows(coords2D)):
        vertex = coords2D[j, :]
        v = template.mapping_function.linear_2.drawing.vertex.add()
        v.id = vert_idx
        vert_idx += 1
        
        x = vertex[0]
        y = vertex[1]
        """TODO: put back when figure out generator error
        if not math.Poly(x).is_linear or not math.Poly(y).is_linear:
            raise Exception("x or y is not linear!")
        """
        
        append_vertex(v.point.x, component, x, template, GLOBALX_2D)
        append_vertex(v.point.y, component, y, template, GLOBALY_2D)
        
        #v.point.x.const = float(math.N(vertex[0]))
        #v.point.y.const = float(math.N(vertex[1]))


    for i in range(math.rows(coords2D)): #edges are from the ordered list of vertices.  If this representation changes, this code must change

        l = i-1
        if l < 0:
            l = math.rows(coords2D) - 1
        h = i

        edge = template.mapping_function.linear_2.drawing.edge.add()
        populate_edge(edge, face.name + "." + str(i), l, h, face.edges[i], template) #TODO: get rid of explicit references to edges?

        #just a little bit of book-keeping...
        append_to_dict( drawing_edge_to_faces, face.edges[i].name, face )

    #face:
    new_face = template.mapping_function.linear_2.drawing.face.add()
    #TODO: Assumption being made that vertices are 0 through num_vertices
    for i in range(math.rows(coords2D)):
        new_face.vertex_id.append(i)


    for i in range(math.rows(coords2D)): #TODO: edges are from the ordered list of vertices.  If this representation changes, this code must change
        l = i-1
        if l < 0:
            l = math.rows(coords2D) - 1
        h = i

        edge_id = name_to_edge_id[face.name + "." + str(i)] #TODO: this is ugly.  Is there a better way of indexing?  Get a real method from Ankur
        new_face.edge_id.append(edge_id)


    new_face.name = face.name
    new_face.id = 0


    
    #3D SECTION
    try:
        #coords3D = math.nsimplify(math.N(math.simplify(math.transpose(face.get3DCoords()))), tolerance = 1e-5)
        #coords3D = math.simplify(math.N(math.nsimplify(math.simplify(math.transpose(face.get3DCoords())), 1e-5)))
        #coords3D = math.simplify(math.nsimplify(math.N(math.transpose(face.get3DCoords()), 1e-5), 1e-5))
        coords3D = math.simplify(math.transpose(face.get3DCoords()))
        print '3d coords are'
        print coords3D
    except Exception:
        print '3d exception'
        coords3D = math.transpose(face.get3DCoords())
        print coords3D
        
    vert_idx = 0
    num_skipped = 0
    for j in range(math.rows(coords3D)):
        vertex = coords3D[j, :]
        v = template.mapping_function.linear_3.mesh.vertex.add()
        v.id = vert_idx
        vert_idx += 1

        x = vertex[0]
        y = vertex[1]
        z = vertex[2]
        
        """TODO: put this back in to handle 0 case
        if (not math.Poly(x).is_linear) or (not math.Poly(y).is_linear) or (not math.Poly(z).is_linear):
            raise Exception("x or y is not linear!")
        """
        
        append_vertex(v.point.x, component, x, template, GLOBALX_3D)
        append_vertex(v.point.y, component, y, template, GLOBALY_3D)
        append_vertex(v.point.z, component, z, template, GLOBALZ_3D)


    #face:
    new_face = template.mapping_function.linear_3.mesh.face.add()

    for i in range(math.rows(coords3D)): #Same number of points in 2D as 3D so this is fine.
        new_face.vertex_id.append(i)

    new_face.name = face.name
    new_face.id = 0
    
    


#TODO: eventually remove clean_up_faces, as it shouldn't actually be needed for this application.
def clean_up_faces(faces):

    for j in range(len(faces)):
        removed_points = []

        face = faces[j]

        for i in range(len(face.pts2d)):
            
            if math.norm( face.get2DCoords()[:, i] - face.get2DCoords()[:, i - 1]) < numerical_error \
            or math.norm( face.get3DCoords()[:, i] - face.get3DCoords()[:, i - 1]) < numerical_error:
                print 'removed point ' + str(i)
                removed_points.append(i)

        face.pts2d = [v for i,v in enumerate(face.pts2d) if i not in removed_points]
        face.edges = [v for i,v in enumerate(face.edges) if i not in removed_points]
    
    
def add_articulation_metadata(articulation, edge, component, template, joint=None):
    if joint is None: #make it a simple revolute.  This section is for backwards compatability.
        #TODO:
        #Add center
        #Add transform
        transform = articulation.transforms.add()
        global control_num
        transform.control.id = control_num; control_num += 1
        transform.control.name = edge.name + ".control" + str(transform.control.id)
        
        
        points =  math.nsimplify(math.simplify(edge.pts3D), tolerance=1e-5)
        

        append_vertex(transform.axis.x, component, math.simplify(points[0][0] - points[1][0]), template) #TODO: something cleaner than template here?
        append_vertex(transform.axis.y, component, math.simplify(points[0][1] - points[1][1]), template)
        append_vertex(transform.axis.z, component, math.simplify(points[0][2] - points[1][2]), template)
        
        append_vertex(articulation.center.x, component, math.simplify((points[0][0] + points[1][0])/2), template)
        append_vertex(articulation.center.y, component, math.simplify((points[0][1] + points[1][1])/2), template)
        append_vertex(articulation.center.z, component, math.simplify((points[0][2] + points[1][2])/2), template)
        
        
        
        
        linearTimeMap = transform.control.inputs.linear_1.linearTimeMap
        linearTimeMap.const = 1 #TODO: for now, dummy velocity
        transform.type = 1
        transform.minVal = -sys.float_info.max #TODO: dummy for now
        transform.maxVal = sys.float_info.max #TODO: dummy for now
    else:
        transform = articulation.transforms.add()
        global control_num
        transform.control.id = control_num; control_num += 1
        transform.control.name = edge.name + ".control" + str(transform.control.id)
        
        pt1 = math.simplify(math.N(edge.pts3D[0], 1e-10)) #TODO: can I write a function similar to _simplify?
        pt2 = math.simplify(math.N(edge.pts3D[0], 1e-10))
        points =  (pt1, pt2)
        
        if joint.axis is None:
            append_vertex(transform.axis.x, component, math.simplify(points[0][0] - points[1][0]), template) #TODO: something cleaner than template here?
            append_vertex(transform.axis.y, component, math.simplify(points[0][1] - points[1][1]), template)
            append_vertex(transform.axis.z, component, math.simplify(points[0][2] - points[1][2]), template)
         
        else:  
            across = None
            for face in edge.faces: #TODO: this won't extend well to more than 2 faces
                if across is None:
                    across = face.getCOM()
                else:
                    across -= face.getCOM()
                    
                    
            along = math.Matrix([math.simplify(points[0][0] - points[1][0]), math.simplify(points[0][1] - points[1][1]), math.simplify(points[0][2] - points[1][2])])
            
            if joint.axis is joint.dirs[0]:
                joint.axis = along

            elif joint.axis is joint.dirs[1]:
                joint.axis = across
            
            elif joint.axis is joint.dirs[2]:
                
                joint.axis = along.cross(across)
            
            

            append_vertex(transform.axis.x, component, math.simplify(joint.axis[0]), template) #TODO: something cleaner than template here?
            append_vertex(transform.axis.y, component, math.simplify(joint.axis[1]), template)
            append_vertex(transform.axis.z, component, math.simplify(joint.axis[2]), template)
        
        append_vertex(articulation.center.x, component, math.simplify((points[0][0] + points[1][0])/2), template)
        append_vertex(articulation.center.y, component, math.simplify((points[0][1] + points[1][1])/2), template)
        append_vertex(articulation.center.z, component, math.simplify((points[0][2] + points[1][2])/2), template)
        
        
        
        #TODO: eventually specify control
        linearTimeMap = transform.control.inputs.linear_1.linearTimeMap
        linearTimeMap.const = 1 #TODO: for now, dummy velocity
        transform.type = 1
        if joint.lowerLimit is not None:
            transform.minVal = float(_simplify(joint.lowerLimit))
        else:
            transform.minVal = -sys.float_info.max #TODO: dummy for now
        if joint.upperLimit is not None:
            joint.maxVal = float(_simplify(joint.upperLimit))
        else:
            transform.maxVal = sys.float_info.max #TODO: dummy for now
    
def convertAngle(angle):
    new_angle = (180.0 - angle) * math.pi / 180.0
    return new_angle


def componentToTemplateProto(component, parent, out):
    #clean_up_faces(graph.faces) TODO: assume okay for now
    
    
    
    graph.place()
    
    #Now constraints:
    addConstraints(component, parent)
    
    #parameterize(component, parent)
    


    for face in graph.faces:
        #first, add a face:
        global template_num #TODO: why was this global needed?
        new_id = template_num
        template_num += 1
        id_to_face[ new_id ] = face
        face_name_to_id[ face.name ] = new_id
        parent.mapping_function.composition.template_id.append(new_id)
        parent.child_template_id.append(new_id)
        face_child_template = out.template.add()
        face_child_template.id = new_id
        

        #Now we clean up the face by pruning edges of length 0:


        #Now that we've created the face as a new child and we've added it, we have to fill it in.
        
        
        populate_face(component, face, face_child_template, parent)

    
    patch_idx = 0
    
    
    

    
    for edge in graph.edges:
        if not edge.name in drawing_edge_to_my_edges:
            continue
        edge_ids = drawing_edge_to_my_edges[edge.name]
        

    
        for face in edge.faces: #TODO: eventually extend this to work for > 2 edges
            angle = edge.faces[face][0]
            edgeType = edge.edgeType
            if angle != 0.0:
                #if len(edge_ids) > 1: TODO: remove?
                #    set_edge_constraints(edge.name, parent)
                angle = convertAngle(angle)
                
                if edgeType == "FOLD":
                    connection = parent.connection.add() #Make a connection
                    connection.connectionMode.foldConnection.angle = float(math.N(angle, 1e-10))
                elif edgeType == "JOINT":
                    connection = parent.connection.add() #Make a connection
                    
                    for joint in edge.joints:
                        
                        connection.connectionMode.jointConnection.angle = float(math.N(angle, 1e-10))
                        add_articulation_metadata(connection.connectionMode.jointConnection.articulations.add(), edge, component, parent, joint) #arbitrary face?
                elif edgeType == "BEND":
                    connection = parent.connection.add() #Make a connection
                    connection.connectionMode.bendConnection.angle = float(math.N(angle, 1e-10))
                for edge_id in edge_ids:
                    patch = my_edge_to_template[edge_id].patch.add()
                    patch.id = patch_idx
                    connection.patchRef.append(patch_idx) #set the connection reference
                    patch_idx += 1
                    patch.edge2SPatch.edgeId = edge_id #and set the patches reference
                    
    
    #stitch up face variables:
    #TODO: this won't work for larger composites
    
    #IPython.embed()
    for key in same_variable:
        same_variable[key] = list(set(same_variable[key]))
        for i in range(len(same_variable[key]) - 1):
            constrain_params(same_variable[key][i], same_variable[key][i + 1], parent)
    #TODO: very hacky
    global same_variable
    #same_variable = {}    
    

def componentToNewTemplateProto(component, out=None, next_id=0):
    
    connections =  []
    if out is None:
        global graph 
        graph = component.composables['graph'] #For convenience
        out = proto.template.TemplateSet()
        out.root_template_id = 0
    template_proto = out.template.add()
    template_proto.id = next_id
    """
    if component.components: #it has subcomponents
        for sub_component in component.components:
            sub_comp_inst = component.components[sub_component][0]
            global template_num
            next_id = template_num
            template_num += 1
            template_proto.mapping_function.composition.template_id.append(next_id)
            template_proto.child_template_id.append(next_id)
            componentToNewTemplateProto(sub_comp_inst, out, next_id)

        set_composition_constraints(component, template_proto, out) #TODO: not completed yet

    else: #It only has faces
        componentToTemplateProto(component, template_proto, out)
    """
    componentToTemplateProto(component, template_proto, out)


    return out

def componentToProtoFile(component, filename, ascii=True):
  global graph 
  graph = component.composables['graph'] #For convenience
  out = componentToNewTemplateProto(component)
  if ascii:
    text_format.PrintMessage(out, open(filename, 'w'), 2)
  else:
    open(filename, 'wb').write(out.SerializeToString())
  
  
