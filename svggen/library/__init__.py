import os, os.path
import glob
import traceback
import logging
# import MySQLdb as db
import sqlite3 as db

from pprint import pprint

from svggen.api.component import Component
from svggen.utils.utils import tryImport


pyComponents = [os.path.basename(f)[:-3] for f in glob.glob(
   os.path.dirname(__file__) + "/*.py") if os.path.basename(f)[0] != "_"]
yamlComponents = [os.path.basename(
   f)[:-5] for f in glob.glob(os.path.dirname(__file__) + "/*.yaml")]
allComponents = list(set(pyComponents + yamlComponents))

def updateComponentsLists():
    pyComponents = [os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__) + "/*.py") if os.path.basename(f)[0] != "_"]
    yamlComponents = [os.path.basename(f)[:-5] for f in glob.glob(os.path.dirname(__file__) + "/*.yaml")]
    allComponents = list(set(pyComponents + yamlComponents))
    # print "\n\n\n\n\nUpdated Components\n", allComponents, "\n\n\n\n"
    return allComponents


def instanceOf(comp, composable_type):
    return composable_type in comp.composables.keys() or composable_type is "all"


# when no arguments are passed in all components are returned
def filterComponents(composable_type=["all"], verbose=False):
    """Summary.
    Creates all the components in the allComponents list, looks through them for
    components which have the specified composable type, and returns a list of those
    Arguments.
        composable_type: An array of keywords corresponding to specific composable
                        types.
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
    for comp in allComponents:
        try:
            a = getComponent(comp, name=comp)
            for ctype in composable_type:
                codeInstance = instanceOf(a, ctype)
                if codeInstance is True and a not in comps:
                    comps.append(a)
            if not verbose:
                print a.getName()
        except Exception as err:
            if verbose is True:
                print "-------------------------------------------------{}".format(comp)
                logging.error(traceback.format_exc())
    return comps


# when no arguments are passed in all components are returned
def filterDatabase(composable_type=["all"], verbose=False):
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
    b = updateComponentsLists()
    # print "Updated components list in filterDatabase==========================="
    # print "\n\n\n\n\n", a, "\n\n\n\n"

    for comp in b:
        try:
            a = queryDatabase(comp)
            # print "component", a
            for ctype in composable_type:
                codeInstance = instanceOf(a, ctype)
                if codeInstance is True and a not in comps:
                    comps.append(a)
        except Exception as err:
            logging.error(traceback.format_exc())

    # print allComponents
    return comps


def getComponent(c, **kwargs):
  try:
    mod = __import__(c, fromlist=[c, "library." + c], globals=globals())
    obj = getattr(mod, c)()
  except ImportError:
    if "baseclass" in kwargs:
      bc = tryImport(kwargs["baseclass"],kwargs["baseclass"])
      obj = bc(os.path.abspath(os.path.dirname(__file__)) + "/" + c + ".yaml")
    else:
      obj = Component(os.path.abspath(os.path.dirname(__file__)) + "/" + c + ".yaml")

  for k, v in kwargs.iteritems():
    if k == 'name':
      obj.setName(v)
    elif k == 'baseclass':
      pass
    else:
      obj.setParameter(k, v)
  if 'name' not in kwargs:
    obj.setName(c)

  return obj


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
    # con = db.connect(user=username, passwd=password)

    # dbPath = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), 'compDatabase.db')
    dbPath = os.path.join(os.getcwd(), 'compDatabase.db')
    print "Database Path", dbPath
    print "Working Directory", os.getcwd()
    con = db.connect(dbPath)
    c = con.cursor()

    initDatabase(c)

    for comp in components:
        print "Component Name: ", comp.getName()
        comp_id = 0
        c.execute('SELECT * FROM components WHERE type LIKE "{}"'.format(comp.getName()))
        # print c.fetchall()
        x = c.fetchall()
        if len(x) == 0:
            c.execute('INSERT INTO components VALUES (NULL, "{}")'.format(comp.getName()))
            c.execute('SELECT LAST_INSERT_ROWID()')
            comp_id = c.fetchall()[0][0]
        else:
            # y = c.fetchall()
            print x, "\n\n\n", x,  "-----------------------"
            comp_id = x[0][0]
        # print "\n\n\n", comp.getName()


        writeInterfaces(comp, comp_id, c)
        writeParameters(comp, comp_id, c)
        writeComposables(comp, comp_id, c)
    # c.close()
    # con.commit()

    con.commit()
    con.close()


def initDatabase(c):
    """Summary.
    Initalizes the database and populates it with the necessary tables.
    Arguments.
        c: cursor object of python database connection object
    Return.
        Nothing
    """
    # c.execute('CREATE DATABASE IF NOT EXISTS component_info')
    # c.execute('USE component_info')
    c.execute('CREATE TABLE IF NOT EXISTS components(id INTEGER PRIMARY KEY AUTOINCREMENT, type VARCHAR(45) NOT NULL DEFAULT "Component")')
    c.execute('CREATE TABLE IF NOT EXISTS interfaces(id INTEGER PRIMARY KEY AUTOINCREMENT, var_name VARCHAR(45) NOT NULL, port_type MEDIUMBLOB NOT NULL)')
    c.execute('CREATE TABLE IF NOT EXISTS params(id INTEGER PRIMARY KEY AUTOINCREMENT, var_name VARCHAR(45) NOT NULL, default_value MEDIUMBLOB NOT NULL)')
    c.execute('CREATE TABLE IF NOT EXISTS composables(id INTEGER PRIMARY KEY AUTOINCREMENT, var_name VARCHAR(45) NOT NULL, composable_obj MEDIUMBLOB NOT NULL)')
    c.execute('CREATE TABLE IF NOT EXISTS component_interface_link(component_id INTEGER NOT NULL, interface_id INTEGER NOT NULL)')
    c.execute('CREATE TABLE IF NOT EXISTS component_parameter_link(component_id INTEGER NOT NULL, parameter_id INTEGER NOT NULL)')
    c.execute('CREATE TABLE IF NOT EXISTS component_composable_link(component_id INTEGER NOT NULL, composable_id INTEGER NOT NULL)')


def writeInterfaces(comp, comp_id, c, verbose=False):
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
    try:
        # delete existing component interface links and interfaces

        c.execute('SELECT * FROM component_interface_link WHERE component_id LIKE {}'.format(comp_id))
        x = c.fetchall()
        if len(x) > 0:
            c.execute('DELETE FROM component_interface_link WHERE component_id LIKE {}'.format(comp_id))
            # print x[0][1]
    except Exception as err:
        logging.error(traceback.format_exc())
    pprint(comp.interfaces)
    for k, v in comp.interfaces.iteritems():
        try:
            value = ""
            if isinstance(v, dict):
                compositeComp = v["subcomponent"]
                value = comp.subcomponents[compositeComp]["component"].interfaces[v["interface"]].__class__.__name__
            else:
                # print comp.interfaces, "\n\n value: ", v
                value = v.__class__.__name__

            c.execute('SELECT * FROM interfaces WHERE var_name LIKE "{}" AND port_type LIKE "{}"'.format(k, value))
            x = c.fetchall()
            if_id = 0
            if len(x) == 0:
                c.execute('INSERT INTO interfaces VALUES (NULL, "{}", "{}")'.format(k, value))
                c.execute('SELECT LAST_INSERT_ROWID()')
                if_id = c.fetchall()[0][0]
            else:
                if_id = x[0][0]

            # Link the interfaces to the component if necessary
            c.execute('SELECT * FROM component_interface_link WHERE component_id LIKE {} AND interface_id LIKE {}'.format(comp_id, if_id))
            x = c.fetchall()
            if len(x) == 0:
                c.execute('INSERT INTO component_interface_link VALUES ({}, {})'.format(comp_id, if_id))

        except Exception as err:
            if verbose is True:
                print "-------------------------------------------------{}".format(comp.getName())
                logging.error(traceback.format_exc())


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
    try:
        # delete existing component interface links and interfaces
        c.execute('SELECT * FROM component_parameter_link WHERE component_id LIKE {}'.format(comp_id))
        x = c.fetchall()
        if len(x) > 0:
            c.execute('DELETE FROM component_parameter_link WHERE component_id LIKE {}'.format(comp_id))
            print x[0][1]
    except Exception as err:
        logging.error(traceback.format_exc())
    pprint(comp.parameters)

    print "Here"

    for k, v in comp.parameters.iteritems():
        print "k:", k, "\tv:", v
        c.execute('SELECT * FROM params WHERE var_name LIKE "{}" AND default_value LIKE "{}"'.format(str(k), str(v)))
        x = c.fetchall()
        print "X: ", x
        param_id = 0
        if len(x) == 0:
            c.execute(
                'INSERT INTO params VALUES (NULL, "{}", "{}")'.format(str(k), str(v)))
            c.execute('SELECT LAST_INSERT_ROWID()')
            param_id = c.fetchall()[0][0]
        else:
            param_id = x[0][0]

        c.execute('SELECT * FROM component_parameter_link WHERE component_id LIKE {} AND parameter_id LIKE {}'.format(comp_id, param_id))
        x = c.fetchall()
        if len(x) == 0:
            c.execute('INSERT INTO component_parameter_link VALUES ({}, {})'.format(comp_id, param_id))


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
        c.execute('SELECT * FROM composables WHERE var_name LIKE "{}" AND composable_obj LIKE "{}"'.format(str(k), str(v.__class__.__name__)))
        x = c.fetchall()
        compos_id = 0
        if len(x) == 0:
            c.execute('INSERT INTO composables VALUES (NULL, "{}", "{}")'.format(str(k), v.__class__.__name__))
            c.execute('SELECT LAST_INSERT_ROWID()')
            compos_id = c.fetchall()[0][0]
        else:
            compos_id = x[0][0]

        print comp_id, compos_id
        c.execute('SELECT * FROM component_composable_link WHERE component_id LIKE {} AND composable_id LIKE {}'.format(comp_id, compos_id))
        x = c.fetchall()
        if len(x) == 0:
            c.execute('INSERT INTO component_composable_link VALUES ({}, {})'.format(comp_id, compos_id))


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
    # con = db.connect(user=username, passwd=password)

    dbPath = os.path.join(os.getcwd(), 'compDatabase.db')
    con = db.connect(dbPath)
    c = con.cursor()
    # c.execute('USE component_info')

    c.execute('SELECT * FROM components WHERE type LIKE "{}"'.format(component))
    exists = c.fetchall()


    # return with error message if the component doesn't exist in the database.
    if len(exists) == 0:
        if verbose:
            print "The component {} is not in the database.\n Call buildDatabase() with this component in the array to update the database. \nIf this message still persists, check if calling getComponent() on this string works.\n".format(component)
        else:
            print "{} not in database".format(component)

        con.commit()
        con.close()
        return None


    # gather interfaces
    item = ComponentQueryItem(component)
    x = c.execute('SELECT c.*, i.* FROM components c INNER JOIN component_interface_link ci ON ci.component_id = c.id INNER JOIN interfaces i ON i.id = ci.interface_id WHERE type LIKE "{}"'.format(component))
    y = c.fetchall()
    item.genInterface(y)

    # gather parameters
    x = c.execute('SELECT c.*, p.* FROM components c INNER JOIN component_parameter_link cp ON cp.component_id = c.id INNER JOIN params p ON p.id = cp.parameter_id WHERE type LIKE "{}"'.format(component))
    y = c.fetchall()
    item.genParameters(y)
    # print y

    # gather composables
    x = c.execute('SELECT c.*, m.* FROM components c INNER JOIN component_composable_link cc ON cc.component_id = c.id INNER JOIN composables m ON m.id = cc.composable_id WHERE type LIKE "{}"'.format(component))
    y = c.fetchall()
    item.genComposables(y)

    # c.close()
    # con.commit()

    con.commit()
    con.close()
    return item

'''import os
import glob

from svggen.api.component import Component
from svggen.utils.utils import tryImport


pyComponents = [ os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__)+"/*.py") if os.path.basename(f)[0] != "_"]
yamlComponents = [ os.path.basename(f)[:-5] for f in glob.glob(os.path.dirname(__file__)+"/*.yaml")]
allComponents = list(set(pyComponents + yamlComponents))

def getComponent(c, **kwargs):
  try:
    mod = __import__(c, fromlist=[c, "library." + c], globals=globals())
    obj = getattr(mod, c)()
  except ImportError:
    if "baseclass" in kwargs:
      bc = tryImport(kwargs["baseclass"],kwargs["baseclass"])
      obj = bc(os.path.abspath(os.path.dirname(__file__)) + "/" + c + ".yaml")
    else:
      obj = Component(os.path.abspath(os.path.dirname(__file__)) + "/" + c + ".yaml")

  for k, v in kwargs.iteritems():
    if k == 'name':
      obj.setName(v)
    elif k == 'baseclass':
      pass
    else:
      obj.setParameter(k, v)
  if 'name' not in kwargs:
    obj.setName(c)

  return obj

# tag : [[required ports], [forbidden ports]]                                                                                                                                       
tagDefinitions = {
  'sensor': [["DataOutputPort"],[]],
  'actuator': [["DataInputPort"],[]],
  'mechanical': [["EdgePort"],[]],
  'device': [["MountPort"],[]],
  'UI': [[],["MountPort", "EdgePort"]]
}

def tag(ports):
  tags = {}
  portset = set(ports.keys())
  for tag, (must, cant) in tagDefinitions.iteritems():
    if set(must).issubset(portset) and not len(set(cant).intersection(portset)):
      tags[tag] = [port for ptype in must for port in ports[ptype] ]
  return tags

_taggedComponents = {}
def getTags(x):
  if x in _taggedComponents:
    return _taggedComponents[x]

  try:
    c = getComponent(x)
  except:
    return None

  if isinstance(c, Component):
    interfaces = c.interfaces.keys()
    ports = {}
    for iname in interfaces:
      i = c.getInterface(iname)
      iclass = i.__class__.__name__
      try:
        ports[iclass].append(iname)
      except KeyError:
        ports[iclass] = [iname]
    _taggedComponents[x] = tag(ports)
    return tag(ports)
  return None

def taggedComponents(components = None):
  if components == None:
    components = allComponents
  for x in components:
    if getTags(x):
      yield x, getTags(x)

def filterComponents(tagList, components = None):
  for x, tags in taggedComponents(components):
    if set(tagList).issubset(set(tags.keys())):
      yield x, [port for tag in tagList for port in tags[tag] ]'''

