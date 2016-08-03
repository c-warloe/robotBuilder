from google.protobuf import text_format

from svggen.api import proto as proto_symbolic
from svggen.api.proto import template_pb2 as proto_template

class proto:
  symbolic = proto_symbolic
  template = proto_template


template_num = 1
face_name_to_id = {}
id_to_face = {}
param_to_id = {}
name_to_edge_id = {}
drawing_edge_to_my_edges = {}
drawing_edge_to_faces = {}
drawing_edge_to_vertices = {}
drawing_edge_is_tab = {}
my_edge_to_template = {}

numerical_error = 0.001 #the maximum numerical error I'm willing to tolerate for adjoining edges
BUFFER = 0.0 #A small buffer to avoid overconstraining the problem due to numerical rounding

def append_to_dict(dictionary, key, value):
    if not key in dictionary:
        dictionary[key] = [value]
    else:
        dictionary[key].append(value)

def populate_parameter(name, default, parameter):
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



def populate_face(component, face, template):
    #First, we add 7 parameters:
    #x, y, w, h
    #3dx, 3dy, 3dz
    global_coords2D = np.dot(face.transform2D, [0,0,0,1])[0:2]
    global_coords3D = np.dot(face.transform3D, [0,0,0,1])[0:3]



    param_x = template.parameter.add()
    populate_parameter(face.name + ".x", global_coords2D[0], param_x) #TODO: set the default value properly - x and y need globals
    param_y = template.parameter.add()
    populate_parameter(face.name+ ".y", global_coords2D[1], param_y)
    param_w = template.parameter.add()
    populate_parameter(face.name + ".w", 1.0, param_w)
    param_h = template.parameter.add()
    populate_parameter(face.name + ".h", 1.0, param_h)
    param_x3d = template.parameter.add()
    populate_parameter(face.name + ".x3d", global_coords3D[0], param_x3d)
    param_y3d = template.parameter.add()
    populate_parameter(face.name + ".y3d", global_coords3D[1], param_y3d)
    param_z3d = template.parameter.add()
    populate_parameter(face.name + ".z3d", global_coords3D[2], param_z3d)

    #2D SECTION
    #Next, we add 2D vertices as functions of these parameters
    vert_idx = 0

    #Vertices
    num_skipped = 0

    for vertex in face.pts2d:


        v = template.mapping_function.linear_2.drawing.vertex.add()
        v.id = vert_idx
        vert_idx += 1
        v.point.x.parameter_id.append( param_to_id[face.name + ".x"] )
        v.point.x.coeff.append(1.0)
        v.point.x.parameter_id.append( param_to_id[face.name + ".w"] )
        v.point.x.coeff.append( vertex[0] )

        v.point.y.parameter_id.append( param_to_id[face.name + ".y"] )
        v.point.y.coeff.append( 1.0 )
        v.point.y.parameter_id.append( param_to_id[face.name + ".h"] )
        v.point.y.coeff.append( vertex[1] )








    for i in range(len(face.pts2d)): #edges are from the ordered list of vertices.  If this representation changes, this code must change

        l = i-1
        if l < 0:
            l = len(face.pts2d) - 1
        h = i

        edge = template.mapping_function.linear_2.drawing.edge.add()
        populate_edge(edge, face.name + "." + str(i), l, h, face.edges[i], template)

        #just a little bit of book-keeping...
        append_to_dict( drawing_edge_to_faces, face.edges[i].name, face )

    #face:
    new_face = template.mapping_function.linear_2.drawing.face.add()
    #TODO: Assumption being made that vertices are 0 through num_vertices
    for i in range(len(face.pts2d)):
        new_face.vertex_id.append(i)


    for i in range(len(face.pts2d)): #TODO: edges are from the ordered list of vertices.  If this representation changes, this code must change
        l = i-1
        if l < 0:
            l = len(face.pts2d) - 1
        h = i

        edge_id = name_to_edge_id[face.name + "." + str(i)] #TODO: this is ugly.  Is there a better way of indexing?  Get a real method from Ankur
        new_face.edge_id.append(edge_id)


    new_face.name = face.name
    new_face.id = 0



    #3D SECTION
    vert_idx = 0
    num_skipped = 0
    for vertex in face.pts2d:
        v = template.mapping_function.linear_3.mesh.vertex.add()
        v.id = vert_idx
        vert_idx += 1

        v.point.x.parameter_id.append( param_to_id[face.name + ".x3d"] )
        v.point.x.coeff.append(1.0)
        v.point.y.parameter_id.append( param_to_id[face.name + ".y3d"] )
        v.point.y.coeff.append(1.0)
        v.point.z.parameter_id.append( param_to_id[face.name + ".z3d"] )
        v.point.z.coeff.append(1.0)

        #local_transform = np.dot(face.transform3D, [vertex[0], vertex[1], 0 ,1])[0:3]


        #So, x = face.transform3D[0, 0] * vertex[0] *width + face.transform3D[0, 1] * vertex[1] * height
        # y = face.transform3D[1, 0] * vertex[0] *width + face.transform3D[1, 1] * vertex[1] * height
        #z = face.transform3D[2, 0] * vertex[0] *width + face.transform3D[2, 1] * vertex[1] * height

        #first x:
        v.point.x.parameter_id.append( param_to_id[face.name + ".w"] )
        v.point.x.coeff.append( face.transform3D[0, 0] * vertex[0] )
        v.point.x.parameter_id.append( param_to_id[face.name + ".h"] )
        v.point.x.coeff.append( face.transform3D[0, 1] * vertex[1] )


        #Second, y:
        v.point.y.parameter_id.append( param_to_id[face.name + ".w"] )
        v.point.y.coeff.append( face.transform3D[1, 0] * vertex[0] )
        v.point.y.parameter_id.append( param_to_id[face.name + ".h"] )
        v.point.y.coeff.append( face.transform3D[1, 1] * vertex[1] )

        #Finally, z:
        v.point.z.parameter_id.append( param_to_id[face.name + ".w"] )
        v.point.z.coeff.append( face.transform3D[2, 0] * vertex[0] )
        v.point.z.parameter_id.append( param_to_id[face.name + ".h"] )
        v.point.z.coeff.append( face.transform3D[2, 1] * vertex[1] )


        #print local_transform
        #v.point.x.const = local_transform[0]
        #v.point.y.const = local_transform[1]
        #v.point.z.const = local_transform[2]

        #TODO: how do I set x, y, and z?



    #face:
    new_face = template.mapping_function.linear_3.mesh.face.add()

    for i in range(len(face.pts2d)): #Same number of points in 2D as 3D so this is fine.
        new_face.vertex_id.append(i)

    new_face.name = face.name
    new_face.id = 0



    #Constraints SECTION
    #TODO: add inherited_id when we figure out what that is
    #TODO: might be easier and more flexible to pass in a list and loop in the future
    #force widths and heights to be positive, as they should be
    new_constraint = template.feasible_set.constraint_list.constraint.add()
    new_constraint.linear_constraint.expr.parameter_id.append( param_to_id[face.name + ".w"] )
    new_constraint.linear_constraint.expr.coeff.append( -1.0 )
    #new_constraint.linear_constraint.expr.const = 1.0 #Debug
    new_constraint.linear_constraint.type = 2 #TODO: is there a way I can directly access the enum for this?

    new_constraint = template.feasible_set.constraint_list.constraint.add()
    new_constraint.linear_constraint.expr.parameter_id.append( param_to_id[face.name + ".h"] )
    new_constraint.linear_constraint.expr.coeff.append( -1.0 )
    #new_constraint.linear_constraint.expr.const = 1.0 #Debug
    new_constraint.linear_constraint.type = 2 #TODO: is there a way I can directly access the enum for this?



def convertAngle(angle):
    new_angle = (180.0 - angle) * np.pi / 180.0
    return new_angle

def get_pairing(points1, points2, vertices):
    if np.linalg.norm(points1[0] - points2[0], 2) < numerical_error and \
        np.linalg.norm(points1[1] - points2[1], 2) < numerical_error: #first try 1, 1 and 2, 2
        return ((vertices[0][0], vertices[1][0]), (vertices[0][1], vertices[1][1]))
    elif np.linalg.norm(points1[0] - points2[1], 2) < numerical_error and \
        np.linalg.norm(points1[1] - points2[0], 2) < numerical_error: #second, try 1, 2 and 2, 1
        return ((vertices[0][0], vertices[1][1]), (vertices[0][1], vertices[1][0]))
    else:
        return None


def set_edge_constraints(edge_name, template, vertices=None, faces=None, create_2d=True):
    #TODO: First, some book-keeping
    #First we get the two pairs of vertices involved
    #Then, we get the two face names involved

    if not vertices:
        vertices = drawing_edge_to_vertices[edge_name]

    if not faces:
        faces = drawing_edge_to_faces[edge_name]


    #Now, let's add constraints - 2 for each vertex pair in 2D, 3 for each vertex in 3D
    #We have two vertex pairs
    #That's 10 constraints all together

    #2D global coords:
    #global_coords1 = np.dot(faces[0].transform2D, [0,0,0,1])[0:2]
    #global_coords2 = np.dot(faces[1].transform2D, [0,0,0,1])[0:2]

    #vertex_11 = np.array( faces[0].pts2d[vertices[0][0]] )
    #vertex_12 = np.array( faces[0].pts2d[vertices[0][1]] )
    #vertex_21 = np.array( faces[1].pts2d[vertices[1][0]] )
    #vertex_22 = np.array( faces[1].pts2d[vertices[1][1]] )


    #point_11 = vertex_11 + global_coords1
    #point_12 = vertex_12 + global_coords1
    #point_21 = vertex_21 + global_coords2
    #point_22 = vertex_22 + global_coords2


    point_11 = np.dot(faces[0].transform3D, [ faces[0].pts2d[vertices[0][0]][0], faces[0].pts2d[vertices[0][0]][1], 0, 1])[0:3]
    point_12 = np.dot(faces[0].transform3D, [ faces[0].pts2d[vertices[0][1]][0], faces[0].pts2d[vertices[0][1]][1], 0, 1])[0:3]
    point_21 = np.dot(faces[1].transform3D, [ faces[1].pts2d[vertices[1][0]][0], faces[1].pts2d[vertices[1][0]][1], 0, 1])[0:3]
    point_22 = np.dot(faces[1].transform3D, [ faces[1].pts2d[vertices[1][1]][0], faces[1].pts2d[vertices[1][1]][1], 0, 1])[0:3]

    pairing = get_pairing((point_11, point_12), (point_21, point_22), vertices)



    if not pairing: #if the pairing is none...
        print 'no pairing :-( '
        return #Don't set up a constraint here.





    #TIME TO MAKE CONSTRAINTS


    #Constrain point 1 x 2d
    #TODO: we don't absolutely need 2D constraints, do we?  That is, if the 3D constraints do the trick.
    if create_2d and not drawing_edge_is_tab[edge_name]:

        constraint = template.feasible_set.constraint_list.constraint.add()

        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".x"] )
        constraint.linear_constraint.expr.coeff.append(1.0)
        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".w"] )
        constraint.linear_constraint.expr.coeff.append( faces[0].transform2D[0, 0] * faces[0].pts2d[pairing[0][0]][0]  )
        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".h"] )
        constraint.linear_constraint.expr.coeff.append(faces[0].transform2D[0, 1] * faces[0].pts2d[pairing[0][0]][1]  )

        #Make sure we include the negative sign!
        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".x"] )
        constraint.linear_constraint.expr.coeff.append(-1.0)
        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".w"] )
        constraint.linear_constraint.expr.coeff.append( -1.0 * faces[1].transform2D[0, 0] * faces[1].pts2d[pairing[0][1]][0]  )
        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".h"] )
        constraint.linear_constraint.expr.coeff.append( -1.0 * faces[1].transform2D[0, 1] * faces[1].pts2d[pairing[0][1]][1]  )
        constraint.linear_constraint.expr.const = BUFFER

        constraint.linear_constraint.type = 1

        #constrain point 1 y 3d
        constraint = template.feasible_set.constraint_list.constraint.add()

        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".y"] )
        constraint.linear_constraint.expr.coeff.append(1.0)
        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".w"] )
        constraint.linear_constraint.expr.coeff.append( faces[0].transform2D[1, 0] * faces[0].pts2d[pairing[0][0]][0]  )
        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".h"] )
        constraint.linear_constraint.expr.coeff.append(faces[0].transform2D[1, 1] * faces[0].pts2d[pairing[0][0]][1]  )

        #Make sure we include the negative sign!
        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".y"] )
        constraint.linear_constraint.expr.coeff.append(-1.0)
        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".w"] )
        constraint.linear_constraint.expr.coeff.append( -1.0 * faces[1].transform2D[1, 0] * faces[1].pts2d[pairing[0][1]][0]  )
        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".h"] )
        constraint.linear_constraint.expr.coeff.append( -1.0 * faces[1].transform2D[1, 1] * faces[1].pts2d[pairing[0][1]][1]  )
        constraint.linear_constraint.expr.const = BUFFER

        constraint.linear_constraint.type = 1

        #Moving onto point 2...
        #constrain point 2 x 3d
        constraint = template.feasible_set.constraint_list.constraint.add()

        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".x"] )
        constraint.linear_constraint.expr.coeff.append(1.0)
        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".w"] )
        constraint.linear_constraint.expr.coeff.append( faces[0].transform2D[0, 0] * faces[0].pts2d[pairing[1][0]][0]  )
        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".h"] )
        constraint.linear_constraint.expr.coeff.append(faces[0].transform2D[0, 1] * faces[0].pts2d[pairing[1][0]][1]  )

        #Make sure we include the negative sign!
        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".x"] )
        constraint.linear_constraint.expr.coeff.append(-1.0)
        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".w"] )
        constraint.linear_constraint.expr.coeff.append( -1.0 * faces[1].transform2D[0, 0] * faces[1].pts2d[pairing[1][1]][0]  )
        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".h"] )
        constraint.linear_constraint.expr.coeff.append( -1.0 * faces[1].transform2D[0, 1] * faces[1].pts2d[pairing[1][1]][1]  )
        constraint.linear_constraint.expr.const = BUFFER

        constraint.linear_constraint.type = 1

        #constrain point 2 y 3d
        constraint = template.feasible_set.constraint_list.constraint.add()

        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".y"] )
        constraint.linear_constraint.expr.coeff.append(1.0)
        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".w"] )
        constraint.linear_constraint.expr.coeff.append( faces[0].transform2D[1, 0] * faces[0].pts2d[pairing[1][0]][0]  )
        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".h"] )
        constraint.linear_constraint.expr.coeff.append(faces[0].transform2D[1, 1] * faces[0].pts2d[pairing[1][0]][1]  )

        #Make sure we include the negative sign!
        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".y"] )
        constraint.linear_constraint.expr.coeff.append(-1.0)
        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".w"] )
        constraint.linear_constraint.expr.coeff.append( -1.0 * faces[1].transform2D[1, 0] * faces[1].pts2d[pairing[1][1]][0]  )
        constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".h"] )
        constraint.linear_constraint.expr.coeff.append( -1.0 * faces[1].transform2D[1, 1] * faces[1].pts2d[pairing[1][1]][1]  )
        constraint.linear_constraint.expr.const = BUFFER

        constraint.linear_constraint.type = 1




    #NEXT UP: 3D

    #constrain point 1 x 3d
    constraint = template.feasible_set.constraint_list.constraint.add()

    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".x3d"] )
    constraint.linear_constraint.expr.coeff.append(1.0)
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".w"] )
    constraint.linear_constraint.expr.coeff.append( faces[0].transform3D[0, 0] * faces[0].pts2d[pairing[0][0]][0]  )
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".h"] )
    constraint.linear_constraint.expr.coeff.append(faces[0].transform3D[0, 1] * faces[0].pts2d[pairing[0][0]][1]  )

    #Make sure we include the negative sign!
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".x3d"] )
    constraint.linear_constraint.expr.coeff.append(-1.0)
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".w"] )
    constraint.linear_constraint.expr.coeff.append( -1.0 * faces[1].transform3D[0, 0] * faces[1].pts2d[pairing[0][1]][0]  )
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".h"] )
    constraint.linear_constraint.expr.coeff.append( -1.0 * faces[1].transform3D[0, 1] * faces[1].pts2d[pairing[0][1]][1]  )
    constraint.linear_constraint.expr.const = BUFFER

    constraint.linear_constraint.type = 1

    #constrain point 1 y 3d
    constraint = template.feasible_set.constraint_list.constraint.add()

    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".y3d"] )
    constraint.linear_constraint.expr.coeff.append(1.0)
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".w"] )
    constraint.linear_constraint.expr.coeff.append( faces[0].transform3D[1, 0] * faces[0].pts2d[pairing[0][0]][0]  )
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".h"] )
    constraint.linear_constraint.expr.coeff.append(faces[0].transform3D[1, 1] * faces[0].pts2d[pairing[0][0]][1]  )

    #Make sure we include the negative sign!
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".y3d"] )
    constraint.linear_constraint.expr.coeff.append(-1.0)
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".w"] )
    constraint.linear_constraint.expr.coeff.append( -1.0 * faces[1].transform3D[1, 0] * faces[1].pts2d[pairing[0][1]][0]  )
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".h"] )
    constraint.linear_constraint.expr.coeff.append( -1.0 * faces[1].transform3D[1, 1] * faces[1].pts2d[pairing[0][1]][1]  )
    constraint.linear_constraint.expr.const = BUFFER

    constraint.linear_constraint.type = 1

    #constrain point 1 z 3d

    constraint = template.feasible_set.constraint_list.constraint.add()

    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".z3d"] )
    constraint.linear_constraint.expr.coeff.append(1.0)
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".w"] )
    constraint.linear_constraint.expr.coeff.append( faces[0].transform3D[2, 0] * faces[0].pts2d[pairing[0][0]][0]  )
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".h"] )
    constraint.linear_constraint.expr.coeff.append(faces[0].transform3D[2, 1] * faces[0].pts2d[pairing[0][0]][1]  )

    #Make sure we include the negative sign!
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".z3d"] )
    constraint.linear_constraint.expr.coeff.append(-1.0)
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".w"] )
    constraint.linear_constraint.expr.coeff.append( -1.0 * faces[1].transform3D[2, 0] * faces[1].pts2d[pairing[0][1]][0]  )
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".h"] )
    constraint.linear_constraint.expr.coeff.append( -1.0 * faces[1].transform3D[2, 1] * faces[1].pts2d[pairing[0][1]][1]  )
    constraint.linear_constraint.expr.const = BUFFER

    constraint.linear_constraint.type = 1




    #Moving onto point 2...
    #constrain point 2 x 3d
    constraint = template.feasible_set.constraint_list.constraint.add()

    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".x3d"] )
    constraint.linear_constraint.expr.coeff.append(1.0)
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".w"] )
    constraint.linear_constraint.expr.coeff.append( faces[0].transform3D[0, 0] * faces[0].pts2d[pairing[1][0]][0]  )
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".h"] )
    constraint.linear_constraint.expr.coeff.append(faces[0].transform3D[0, 1] * faces[0].pts2d[pairing[1][0]][1]  )

    #Make sure we include the negative sign!
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".x3d"] )
    constraint.linear_constraint.expr.coeff.append(-1.0)
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".w"] )
    constraint.linear_constraint.expr.coeff.append( -1.0 * faces[1].transform3D[0, 0] * faces[1].pts2d[pairing[1][1]][0]  )
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".h"] )
    constraint.linear_constraint.expr.coeff.append( -1.0 * faces[1].transform3D[0, 1] * faces[1].pts2d[pairing[1][1]][1]  )
    constraint.linear_constraint.expr.const = BUFFER

    constraint.linear_constraint.type = 1

    #constrain point 2 y 3d
    constraint = template.feasible_set.constraint_list.constraint.add()

    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".y3d"] )
    constraint.linear_constraint.expr.coeff.append(1.0)
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".w"] )
    constraint.linear_constraint.expr.coeff.append( faces[0].transform3D[1, 0] * faces[0].pts2d[pairing[1][0]][0]  )
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".h"] )
    constraint.linear_constraint.expr.coeff.append(faces[0].transform3D[1, 1] * faces[0].pts2d[pairing[1][0]][1]  )

    #Make sure we include the negative sign!
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".y3d"] )
    constraint.linear_constraint.expr.coeff.append(-1.0)
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".w"] )
    constraint.linear_constraint.expr.coeff.append( -1.0 * faces[1].transform3D[1, 0] * faces[1].pts2d[pairing[1][1]][0]  )
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".h"] )
    constraint.linear_constraint.expr.coeff.append( -1.0 * faces[1].transform3D[1, 1] * faces[1].pts2d[pairing[1][1]][1]  )
    constraint.linear_constraint.expr.const = BUFFER

    constraint.linear_constraint.type = 1

    #constrain point 2 z 3d
    constraint = template.feasible_set.constraint_list.constraint.add()

    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".z3d"] )
    constraint.linear_constraint.expr.coeff.append(1.0)
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".w"] )
    constraint.linear_constraint.expr.coeff.append( faces[0].transform3D[2, 0] * faces[0].pts2d[pairing[1][0]][0]  )
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[0].name + ".h"] )
    constraint.linear_constraint.expr.coeff.append(faces[0].transform3D[2, 1] * faces[0].pts2d[pairing[1][0]][1]  )

    #Make sure we include the negative sign!
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".z3d"] )
    constraint.linear_constraint.expr.coeff.append(-1.0)
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".w"] )
    constraint.linear_constraint.expr.coeff.append( -1.0 * faces[1].transform3D[2, 0] * faces[1].pts2d[pairing[1][1]][0]  )
    constraint.linear_constraint.expr.parameter_id.append( param_to_id[faces[1].name + ".h"] )
    constraint.linear_constraint.expr.coeff.append( -1.0 * faces[1].transform3D[2, 1] * faces[1].pts2d[pairing[1][1]][1]  )
    constraint.linear_constraint.expr.const = BUFFER

    constraint.linear_constraint.type = 1


def clean_up_faces(faces):


    for j in range(len(faces)):
        removed_points = []

        face = faces[j]



        for i in range(len(face.pts2d)):
            if np.norm( face.get2DCoords()[:, i] - face.get2DCoords()[:, i - 1], 2) < numerical_error \
            or np.norm( face.get3DCoords()[:, i] - face.get3DCoords()[:, i - 1], 2) < numerical_error:
                print 'removed point ' + str(i)
                removed_points.append(i)

        face.pts2d = [v for i,v in enumerate(face.pts2d) if i not in removed_points]
        face.edges = [v for i,v in enumerate(face.edges) if i not in removed_points]





def componentToTemplateProto(component, parent, out):
    #first, let's make the child template calls.
    #We need to iterate over all the faces



    clean_up_faces(component.graph.faces)

    component.graph.place()

    for face in component.graph.faces:
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

        populate_face(component, face, face_child_template)


    patch_idx = 0
    for edge in component.graph.edges:
        if not edge.name in drawing_edge_to_my_edges:
            continue
        edge_ids = drawing_edge_to_my_edges[edge.name]


        for face in edge.faces: #TODO: eventually extend this to work for > 2 edges
            angle = edge.faces[face][0]
            if angle != 0.0:
                if len(edge_ids) > 1:
                    set_edge_constraints(edge.name, parent)
                angle = convertAngle(angle)
                connection = parent.connection.add() #Make a connection
                connection.connectionMode.foldConnection.angle = angle
                for edge_id in edge_ids:
                    patch = my_edge_to_template[edge_id].patch.add()
                    patch.id = patch_idx
                    connection.patchRef.append(patch_idx) #set the connection reference
                    patch_idx += 1
                    patch.edge2SPatch.edgeId = edge_id #and set the patches reference





        #print edge.name
        #print edge_id


    print "Done!  Happy Robutting!"

def set_composition_constraints(component, template_proto, out): #TODO: for now just setting edges.  In the future, should generalize to faces, etc.
    #First, get all the connections
    for connection in component.connections:
        try:

            edge1 = component.getInterfaces(connection[0][0], connection[0][1])
            edge2 = component.getInterfaces(connection[1][0], connection[1][1])
            #edge1 = component.components[connection[0][0]][0].interfaces[ connection[0][1] ]
            #edge2 = component.components[connection[1][0]][0].interfaces[ connection[1][1] ]

        except Exception:
            print 'key error warning'
            continue


        #potential ankur bug handling
        if type(edge1) is list:
            edge1 = edge1[0]
        if type(edge2) is list:
            edge2 = edge2[0]

        full_edge1 = connection[0][0] + "." + edge1
        full_edge2 = connection[1][0] + "." + edge2

        try:
            vertices1 = drawing_edge_to_vertices[full_edge1]
            faces1 = drawing_edge_to_faces[full_edge1]
            set_edge_constraints(full_edge1, template_proto, vertices1, faces1, False)
        except Exception:
            pass

        try:
            vertices2 = drawing_edge_to_vertices[full_edge2]
            faces2 = drawing_edge_to_faces[full_edge2]
            set_edge_constraints(full_edge2, template_proto, vertices2, faces2, False)
        except Exception:
            pass



def componentToNewTemplateProto(component, out=None, next_id=0):
    connections =  []
    if out is None:
        out = proto.template.TemplateSet()
        out.root_template_id = 0
    template_proto = out.template.add()
    template_proto.id = next_id
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


    return out


def componentToProtoFile(component, filename, ascii=False):
  out = componentToNewTemplateProto(component)
  if ascii:
    text_format.PrintMessage(out, open(filename, 'w'), 2)
  else:
    open(filename, 'wb').write(out.SerializeToString())
