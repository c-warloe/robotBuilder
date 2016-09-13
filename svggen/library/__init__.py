import os
import glob
import traceback
import logging
import MySQLdb as db
import pickle
import copy_reg
import types
from svggen.api.component import Component


pyComponents = [os.path.basename(f)[:-3] for f in glob.glob(
    os.path.dirname(__file__) + "/*.py") if os.path.basename(f)[0] != "_"]
yamlComponents = [os.path.basename(
    f)[:-5] for f in glob.glob(os.path.dirname(__file__) + "/*.yaml")]


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

allComponents = list(set(pyComponents + yamlComponents))

def reduce_method(m):
    return (getattr, (m.__self__, m.__func__.__name__))

copy_reg.pickle(types.MethodType, reduce_method)

def instanceOf(comp, composable_type):
    return composable_type in comp.composables.keys() or composable_type is "all"


# when no arguments are passed in all components are returned
def filterComponents(composable_type="all"):
    """Summary.
    Creates all the components in the allComponents list, looks through them for
    components which have the specified composable type, and returns a list of those

    Arguments.
        composable_type: The keyword corresponding to a specific composable type.
                         ex: "code" for "CodeComposable"

                         To view the possible strings for composable_type, call
                         filterComponents with its default parameter and look at
                         the key values of Component.composables for all the
                         Component objects in the array the function returns.

                         Default value is "all". This populates the array with
                         ComponentQueryItems of related to all composables.
    Return.
        Array of Component objects which have the specified composable type
    """
    comps = []
    for comp in pyComponents:
        try:
            a = getComponent(comp, name=comp)
            codeInstance = instanceOf(a, composable_type)
            if codeInstance is True:
                comps.append(a)
                # print comp
        except Exception as err:
            print "-------------------------------------------------{}".format(comp)
            logging.error(traceback.format_exc())
    return comps


# when no arguments are passed in all components are returned
def filterDatabase(composable_type="all"):
    """Summary.
    Looks through database for components which have the specified composable type

    Arguments.
        composable_type: The keyword corresponding to a specific composable type.
                         ex: "code" for "CodeComposable"
                         Default value is "all". This populates the array with
                         ComponentQueryItems of related to all composables.
    Return.
        Array of ComponentQueryItems populated with all the components in the
        database which had the specified composable type
    """
    comps = []
    for comp in allComponents:
        try:
            a = queryDatabase(comp)
            codeInstance = instanceOf(a, composable_type)
            if codeInstance is True:
                comps.append(a)
                # print comp
        except Exception as err:
            pass
    return comps


def getComponent(c, remake=False, **kwargs):
    if not remake:
        obj = getFromFile(c)
        if obj:
            return obj

    try:
        mod = __import__(c, fromlist=[c, "library." + c], globals=globals())
        obj = getattr(mod, c)()
    except ImportError as inst:
        obj = Component(os.path.abspath(
            os.path.dirname(__file__)) + "/" + c + ".yaml")

    for k, v in kwargs.iteritems():
        if k == 'name':
            obj.setName(v)
        elif not 'remake':
            obj.setParameter(k, v)
        else:
            continue
    if 'name' not in kwargs:
        obj.setName(c)
    serializeToFile(obj,c, remake)
    return obj


def getFromFile(name):
    if not os.path.isfile(os.path.join(__location__, name+".dat")):
        return False
    datFile = open(os.path.join(__location__, name+".dat"), 'rb')
    component = pickle.load(datFile)
    datFile.close()
    return component

def serializeToFile(component, name, overwrite=False):
    if os.path.isfile(os.path.join(__location__, name+".dat")) and not overwrite:
        raise Exception('File already exists with name: '+ name)
    datFile = open(os.path.join(__location__, name+".dat"), 'wb')
    pickle.dump(component,datFile)
    datFile.close()




def buildDatabase(components, username="root", password=""):
    """Summary.
    Saves critical data about the passed in components in the database.
    Use with filterComponents()

    Arguments.
        components: An array of Component objects that will be saved to the
                    database
        username: Username for the MySQL server. Default is "root" (STRING)
        password: Password for the MySQL server. Default is empty string "" (STRING)
    Return.
        Nothing
    """
    con = db.connect(user=username, passwd=password)
    c = con.cursor()

    initDatabase(c)

    for comp in components:
        comp_id = 0
        x = c.execute(
            'SELECT * FROM components WHERE type LIKE "{}"'.format(comp.getName()))
        if x == 0:
            c.fetchall()
            c.execute(
                'INSERT INTO components VALUES (NULL, "{}")'.format(comp.getName()))
            c.execute('SELECT LAST_INSERT_ID()')
            comp_id = c.fetchall()[0][0]
        else:
            y = c.fetchall()
            comp_id = y[0][0]
        print "\n\n\n", comp.getName()

        writeInterfaces(comp, comp_id, c)
        writeParameters(comp, comp_id, c)
        writeComposables(comp, comp_id, c)
    c.close()
    con.commit()


def initDatabase(c):
    """Summary.
    Initalizes the database and populates it with the necessary tables.

    Arguments.
        c: cursor object of python database connection object
    Return.
        Nothing
    """
    c.execute('CREATE DATABASE IF NOT EXISTS component_info')
    c.execute('USE component_info')
    c.execute('CREATE TABLE IF NOT EXISTS components(id INTEGER AUTO_INCREMENT, type VARCHAR(45) NOT NULL DEFAULT "Component", PRIMARY KEY(id))')
    c.execute('CREATE TABLE IF NOT EXISTS interfaces(id INTEGER AUTO_INCREMENT, var_name VARCHAR(45) NOT NULL, port_type MEDIUMBLOB NOT NULL, PRIMARY KEY(id))')
    c.execute('CREATE TABLE IF NOT EXISTS params(id INTEGER AUTO_INCREMENT, var_name VARCHAR(45) NOT NULL, default_value MEDIUMBLOB NOT NULL, PRIMARY KEY(id))')
    c.execute('CREATE TABLE IF NOT EXISTS composables(id INTEGER AUTO_INCREMENT, var_name VARCHAR(45) NOT NULL, composable_obj MEDIUMBLOB NOT NULL, PRIMARY KEY(id))')
    c.execute('CREATE TABLE IF NOT EXISTS component_interface_link(component_id INTEGER NOT NULL, interface_id INTEGER NOT NULL)')
    c.execute('CREATE TABLE IF NOT EXISTS component_parameter_link(component_id INTEGER NOT NULL, parameter_id INTEGER NOT NULL)')
    c.execute('CREATE TABLE IF NOT EXISTS component_composable_link(component_id INTEGER NOT NULL, composable_id INTEGER NOT NULL)')


def writeInterfaces(comp, comp_id, c):
    """Summary.
    Writes all the interfaces of a component to the database. If a component is
    composite, recursion is used to link the interfaces of subcomponents with
    the one passed in as an argument.

    Arguments.
        comp: Component object
        comp_id: Primary key id of the component object in the database (INTEGER)
        c: cursor object of python database connection object
    Return.
        Nothing
    """
    for k, v in comp.interfaces.iteritems():
        value = ""
        if isinstance(v, dict):
            compositeComp = v["subcomponent"]
            value = comp.subcomponents[compositeComp][
                "component"].interfaces[k].__class__.__name__
        else:
            value = v.__class__.__name__
        x = c.execute(
            'SELECT * FROM interfaces WHERE var_name LIKE "{}" AND port_type LIKE "{}"'.format(k, value))
        if_id = 0
        if x == 0:
            c.fetchall()
            c.execute(
                'INSERT INTO interfaces VALUES (NULL, "{}", "{}")'.format(k, value))
            c.execute('SELECT LAST_INSERT_ID()')
            if_id = c.fetchall()[0][0]
        else:
            y = c.fetchall()
            if_id = y[0][0]

        # Link the interfaces to the component if necessary
        x = c.execute(
            'SELECT * FROM component_interface_link WHERE component_id LIKE {} AND interface_id LIKE {}'.format(comp_id, if_id))
        if x == 0:
            c.fetchall()
            c.execute(
                'INSERT INTO component_interface_link VALUES ({}, {})'.format(comp_id, if_id))
        else:
            c.fetchall()


def writeParameters(comp, comp_id, c):
    """Summary.
    Writes all the parameters of a component to the database.

    Arguments.
        comp: Component object
        comp_id: Primary key id of the component object in the database (INTEGER)
        c: cursor object of python database connection object
    Return.
        Nothing
    """
    for k, v in comp.parameters.iteritems():
        x = c.execute(
            'SELECT * FROM params WHERE var_name LIKE "{}" AND default_value LIKE "{}"'.format(str(k), str(v)))
        param_id = 0
        if x == 0:
            c.fetchall()
            c.execute(
                'INSERT INTO params VALUES (NULL, "{}", "{}")'.format(str(k), str(v)))
            c.execute('SELECT LAST_INSERT_ID()')
            param_id = c.fetchall()[0][0]
        else:
            y = c.fetchall()
            param_id = y[0][0]

        x = c.execute(
            'SELECT * FROM component_parameter_link WHERE component_id LIKE {} AND parameter_id LIKE {}'.format(comp_id, param_id))
        if x == 0:
            c.fetchall()
            c.execute(
                'INSERT INTO component_parameter_link VALUES ({}, {})'.format(comp_id, param_id))
        else:
            c.fetchall()


def writeComposables(comp, comp_id, c):
    """Summary.
    Writes all the composables associated with a component to the database.

    Arguments.
        comp: Component object
        comp_id: Primary key id of the component object in the database (INTEGER)
        c: cursor object of python database connection object
    Return.
        Nothing
    """
    for k, v in comp.composables.iteritems():
        x = c.execute(
            'SELECT * FROM composables WHERE var_name LIKE "{}" AND composable_obj LIKE "{}"'.format(str(k), str(v.__class__.__name__)))
        compos_id = 0
        if x == 0:
            c.fetchall()
            c.execute(
                'INSERT INTO composables VALUES (NULL, "{}", "{}")'.format(str(k), str(v.__class__.__name__)))
            c.execute('SELECT LAST_INSERT_ID()')
            compos_id = c.fetchall()[0][0]
        else:
            y = c.fetchall()
            compos_id = y[0][0]

        x = c.execute(
            'SELECT * FROM component_composable_link WHERE component_id LIKE {} AND composable_id LIKE {}'.format(comp_id, compos_id))
        if x == 0:
            c.fetchall()
            c.execute(
                'INSERT INTO component_composable_link VALUES ({}, {})'.format(comp_id, compos_id))
        else:
            c.fetchall()


class ComponentQueryItem:

    def __init__(self, name):
        """Summary.
        Initialize ComponentQueryItem

        Arguments.
            name: The name of the component. The value returned when
                  Component.getName() is called. (STRING)
        Return.
            ComponentQueryItem
        Attributes.
            name: The name of the component. The value returned when
                  Component.getName() is called. (STRING)
            interfaces: A dictionary containing the variable names of the
                        interfaces as its keys and the type of interface as its
                        values. All the data in the dict are strings
            parameters: A dictionary containing the variable names of the
                        parameters as its keys and the default values of the
                        parameters as its values. All the keys in the dict are
                        strings and all the values are string representations of
                        the default parameter values
            composables: A dictionary containing the types of the composables as
                         its keys and the names of the corresponding Composable
                         classes as its values. All the data in the dict are
                         strings
        """
        self.name = name

        # format: {interfaceName1 : interfaceType1, interfaceName2 :
        # interfaceType2}
        self.interfaces = {}

        # format: {parameterName1 : parameterValue1, parameterName2 :
        # parameterValue2}
        self.parameters = {}

        # format: {composableName1 : composableValue1, composableName2 :
        # composableValue2}
        self.composables = {}

    def genInterface(self, rows):
        for i in rows:
            self.interfaces[i[3]] = i[4]

    def genParameters(self, rows):
        for i in rows:
            self.parameters[i[3]] = i[4]

    def getName(self):
        return self.name

    def genComposables(self, rows):
        for i in rows:
            self.composables[i[3]] = i[4]


def queryDatabase(component, username="root", password="", verbose=False):
    """Summary.
    Look through the database and get a ComponentQueryItem that corresponds to
    component Object required

    Arguments.
        component: The name of the component. The value returned when
                   Component.getName() is called. (STRING)
        username: Username for the MySQL server. Default is "root" (STRING)
        password: Password for the MySQL server. Default is empty string "" (STRING)
        verbose: If True, the function outputs a more detailed error message when
                 a databse query fails. Default is False. (BOOLEAN)
    Return.
        ComponentQueryItem
    """
    con = db.connect(user=username, passwd=password)
    c = con.cursor()
    c.execute('USE component_info')
    exists = c.execute(
        'select *from components where type like "{}"'.format(component))

    # return with error message if the component doesn't exist in the database.
    if exists == 0:
        if verbose:
            print "The component {} is not in the database.\n Call buildDatabase() with this component in the array to update the database. \nIf this message still persists, check if calling getComponent() on this string works.\n".format(component)
        else:
            print "{} not in database".format(component)
        c.fetchall()
        c.close()
        con.commit()
        return None

    c.fetchall()

    # gather interfaces
    item = ComponentQueryItem(component)
    x = c.execute('SELECT c.*, i.* FROM components c INNER JOIN component_interface_link ci ON ci.component_id = c.id INNER JOIN interfaces i ON i.id = ci.interface_id WHERE type LIKE "{}"'.format(component))
    y = c.fetchall()
    item.genInterface(y)

    # gather parameters
    x = c.execute('SELECT c.*, p.* FROM components c INNER JOIN component_parameter_link cp ON cp.component_id = c.id INNER JOIN params p ON p.id = cp.parameter_id WHERE type LIKE "{}"'.format(component))
    y = c.fetchall()
    item.genParameters(y)

    # gather composables
    x = c.execute('SELECT c.*, m.* FROM components c INNER JOIN component_composable_link cc ON cc.component_id = c.id INNER JOIN composables m ON m.id = cc.composable_id WHERE type LIKE "{}"'.format(component))
    y = c.fetchall()
    item.genComposables(y)

    c.close()
    con.commit()
    return item

