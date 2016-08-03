__author__ = 'Joseph'
import ntpath
import os
from svggen import SVGGEN_DIR
from Composable import Composable
from collections import OrderedDict

from svggen.api.ports.DataOutputPort import DataOutputPort
from svggen.api.ports.DataInputPort import DataInputPort
from svggen.api.ports.DataPort import DataPort

class CodeComposable(Composable):
  def new(self):
    return self.__class__()

  def __init__(self):
    # Set up info to store incrementally during addInterface and attach
    self._components = OrderedDict()         # Map from processed components to their pins
    self._controllerDirs = {}     # Map from known controllers to a folder we created for its temp code
    self._virtualPins = []        # List of ports, indexed by assigned virtual pin
    self._dataMap = OrderedDict() # Map from data output ID to list of connected input IDs
    self._hFilename = 'robotLibrary.h'
    self._cFilename = 'robotLibrary.cpp'

    # Set up location for partially processed code (incrementally processed during add / attach)
    self._tempOutputDir = 'tempOutput/'  # Place to put partly-processed code
    self._methodsDir = 'methods/'
    self._insertionsDir = 'insertions/'
    self._declarationsFile = 'declarations.txt'

    # Clear temp output directory
    if not os.path.exists(self._tempOutputDir):
      os.mkdir(self._tempOutputDir)

  # Check if we have already seen the given interface (may have clone of it)
  def haveInterface(self, interface, list=None):
    return self.getInterface(interface, list) is not None

  def getInterface(self, interface, list=None):
    toCheck = self._virtualPins if list is None else list
    for storedInterface in toCheck:
      if storedInterface.getParent() is interface.getParent() and storedInterface.getName() == interface.getName():
        return storedInterface
    return None

  # Learn about a new component in the design
  def addComponent(self, component):
    if component in self._components:
      return
    self._components[component] = []
    # Process its code
    try: # will throw exception if not a CodeComponent
      codeFiles = component.getCodeFiles()
      controller = component.getParameter('controller', strict=False)
      for codeFile in codeFiles:
        self._processCodeFile(codeFile, controller, component)
    except AttributeError:
      pass

  # Learn about a new interface in the design
  def addInterface(self, newInterface):
    if self.haveInterface(newInterface):
      return
    res = 'addInterface for ' + newInterface.getParent().getName() + '.' + newInterface.getName()
    # Update some state based on new port and its parent
    self._virtualPins.append(newInterface)
    if isinstance(newInterface, DataOutputPort):
      self._dataMap[len(self._virtualPins)-1] = []
    newParent = newInterface.getParent()
    if newParent in self._components:
      self._components[newParent].append(newInterface)
      res += '\n\talready seen its code'
    self.addComponent(newParent)
    #print res

  # Learn about a new connection
  def attach(self, selfInterface, newInterface, kwargs):
    self.addInterface(selfInterface)
    self.addInterface(newInterface)
    # Update data map if the ports are data ports
    if isinstance(selfInterface, DataPort) and isinstance(newInterface, DataPort):
      storedSelfInterface = self.getInterface(selfInterface)
      storedNewInterface = self.getInterface(newInterface)
      selfPin = self._virtualPins.index(storedSelfInterface)
      newPin = self._virtualPins.index(storedNewInterface)
      if isinstance(selfInterface, DataOutputPort) and isinstance(newInterface, DataInputPort):
        if selfPin not in self._dataMap:
          self._dataMap[selfPin] = [newPin]
        elif newPin not in self._dataMap[selfPin]:
          self._dataMap[selfPin].append(newPin)
      elif isinstance(newInterface, DataOutputPort) and isinstance(selfInterface, DataInputPort):
        if newPin not in self._dataMap:
          self._dataMap[newPin] = [selfPin]
        elif selfPin not in self._dataMap[newPin]:
          self._dataMap[newPin].append(selfPin)

  # Update our state based on another composable
  def append(self, newComposable, newPrefix):
    newState = newComposable.getState()
    #print 'append'
    for (component, ports) in newState[0].iteritems():
      if component not in self._components:
        self._components[component] = ports[:]
      else:
        for port in ports:
          if port not in self._components[component]:
            self._components[component].append(port)
    for pin in newState[1]:
      if pin not in self._virtualPins:
        self._virtualPins.append(pin)
    #print 'other data map is ', newState[2]
    #print 'my data map is', self._dataMap
    for (newStateOutID, newStateInIDs) in newState[2].iteritems():
      outPort = newState[1][newStateOutID]
      outID = self._virtualPins.index(outPort)
      if outID not in self._dataMap:
        self._dataMap[outID] = []
      for newStateInID in newStateInIDs:
        inPort = newState[1][newStateInID]
        inID = self._virtualPins.index(inPort)
        if inID not in self._dataMap[outID]:
          self._dataMap[outID].append(inID)
    for (k, v) in newState[3].iteritems():
      if k not in self._controllerDirs:
        self._controllerDirs[k] = v

  def getState(self):
    return [self._components, self._virtualPins,
            self._dataMap, self._controllerDirs]

  # Make the final output
  def makeOutput(self, filedir, **kwargs):
    a = None
    tab = '  '
    res = '\nCodeComposable MakeOutput'
    # Loop through all known controllers for which we need to generate code
    for (controller, controllerDir) in self._controllerDirs.iteritems():
      if controller is not None:
        mainName = 'code_for_' + controller.getName().replace(' ', '_')
      else:
        mainName = 'code_for_None'
      res += '\nProcessing ' + mainName
      outDir = filedir + '/' + mainName + '/'
      # Clear output directory
      if os.path.exists(outDir):
        for root, dirs, files in os.walk(outDir, topdown=False):
          for name in files:
            os.remove(os.path.join(root, name))
          for name in dirs:
            os.rmdir(os.path.join(root, name))
      else:
        os.mkdir(outDir)
      # Process code files from the controller
      if controller is not None:
        for codeFile in controller.getCodeFiles():
          self._processCodeFile(codeFile, controller, None)
      # Process general robot code files needed for any controller
      self._processCodeFile(self._codePath('code/robot_code.cpp'), controller, None)
      if len(self._dataMap) > 0:
        self._processCodeFile(self._codePath('code/data_flow.cpp'), controller, None)

      # Copy main file to the output directory, renaming it to mainName
      # Also add include statement for our new h file
      for root, dirs, files in os.walk(controllerDir, topdown=False):
        for name in files:
          if '__mainCodeFile__' in name:
            mainName = mainName + name[-4:]
            fin = open(os.path.join(root, name), 'r')
            fout = open(outDir + mainName, 'w+')
            fout.write('#include \"' + self._hFilename + '\"')
            fout.write(fin.read())
            fin.close()
            fout.close()
            os.remove(os.path.join(root, name))

      hout = open(outDir + self._hFilename, 'w+')
      hout.write('#ifndef INCL_' + self._hFilename.replace('.', '_').upper() + '\n')
      hout.write('#define INCL_' + self._hFilename.replace('.', '_').upper() + '\n\n')
      cout = open(outDir + self._cFilename, 'w+')
      cout.write('#include \"' + self._hFilename + '\"' + '\n\n')

      # Write the copied declarations
      # into header file if preprocessor directives, otherwise into cpp file
      res += '\n\tProcessing declarations...'
      fin = open(controllerDir + self._declarationsFile, 'r')
      declarations = fin.read().strip()
      fin.close()
      declarations = self._processTags(declarations)
      for line in declarations.splitlines(True):
        line = line.strip() + '\n'
        if len(line) > 0:
          if '#' == line[0]:
            hout.write(line)
          else:
            cout.write(line)
          # If it is a local include statement, try to find and copy that file
          if '#include \"' in line:
            includeFile = line[line.find('\"')+1:line.rfind('\"')]
            includeFileBase = includeFile[0:includeFile.rfind('.')]
            for filename in [includeFile, includeFileBase + '.cpp', includeFileBase + '.c']:
              if(os.path.exists(self._codePath('code/' + filename))):
                incOut = open(outDir + filename, 'w+')
                incIn = open(self._codePath('code/' + filename), 'r')
                incOut.write(incIn.read())
                incOut.close()
                incIn.close()
          # If it is any type of include statement, insert in main file as well
          if '#include' in line:
            fin = open(outDir + mainName, 'r')
            mainContents = fin.read()
            fin.close()
            fout = open(outDir + mainName, 'w')
            fout.write(line)
            fout.write(mainContents)
            fout.close()

      os.remove(controllerDir + self._declarationsFile)

      # Write method declarations into the header file
      hout.write('\n')
      for root, dirs, files in os.walk(controllerDir + self._methodsDir, topdown=False):
        for name in files:
          name = name[0:-4]
          name = name.replace('^', '*')
          name += ';'
          hout.write('\n' + name)
      hout.write('\n\n#endif')
      hout.close()

      # Write the methods into the cpp file, making insertions as appropriate
      res += '\n\tProcessing methods...'
      for root, dirs, files in os.walk(controllerDir + self._methodsDir, topdown=False):
        for name in files:
          # Read the method body
          res += '\n\t\tSee method ' + name
          fin = open(os.path.join(root, name), 'r')
          method = fin.read()
          fin.close()
          # See if there are insertions into this method
          for postName in ['', '@prepend', '@append']:
            if os.path.exists(controllerDir + self._insertionsDir + '/' + name[0:-4] + postName + '.txt'):
              fin = open(controllerDir + self._insertionsDir + '/' + name[0:-4] + postName + '.txt', 'r')
              insertion = fin.read()
              res += '\n\t\tSee ' + postName + ' insertion\n\t\t\t' + insertion.strip().replace('\n', '\n\t\t\t')
              fin.close()
              if 'prepend' in postName:
                methodPre = method[0:method.find('{')+1].strip()
                methodPost = method[method.find('{')+1:].strip()
                method = methodPre + '\n' + tab
                method += insertion.strip().replace('\n', '\n' + tab)
                method += '\n' + tab + methodPost
              else:
                method = method[0:method.rfind('}')].strip()
                insertion = insertion.strip()
                method += '\n' + tab
                method += insertion.strip().replace('\n', '\n' + tab)
                method += '\n}'
              os.remove(controllerDir + self._insertionsDir + '/' + name[0:-4] + postName + '.txt')
          method = self._processTags(method)
          cout.write('\n\n' + method)
          os.remove(os.path.join(root, name))
      cout.close()
      os.rmdir(controllerDir + self._methodsDir)

      # Any insertions left over probably go into the main file
      res += '\n\tProcessing leftover insertions...'
      for root, dirs, files in os.walk(controllerDir + self._insertionsDir, topdown=False):
        for name in files:
          res += '\n\t\tsee insertion into ' + name
          methodName = name[:-4]
          append = True
          if '@prepend' in methodName:
            methodName = methodName[0:methodName.find('@prepend')]
            append = False
          if '@append' in methodName:
            methodName = methodName[0:methodName.find('@append')]
          fin = open(os.path.join(root, name))
          insertion = fin.read()
          fin.close()
          insertion = self._processTags(insertion)
          # If this is in the main file, make the insertion
          if os.path.exists(outDir + mainName):
            fin = open(outDir + mainName, 'r')
            mainFile = fin.read()
            fin.close()
            if methodName in mainFile:
              fout = open(outDir + mainName, 'w+')
              lines = mainFile.splitlines(True)
              lineNum = 0
              line = lines[lineNum]
              while methodName not in line:
                fout.write(line)
                lineNum += 1
                line = lines[lineNum]
              while '{' not in line:
                fout.write(line)
                lineNum += 1
                line = lines[lineNum]
              fout.write(line[0:line.find('{')+1])
              # have now copied everything up to and including the '{'
              if '}' not in line:
                methodBody = line[line.find('{')+1:]
                lineNum += 1
                line = lines[lineNum]
                while '}' not in line:
                  methodBody += line
                  lineNum += 1
                  line = lines[lineNum]
                methodBody += line[0:line.find('}')]
              else:
                methodBody = line[line.find('{')+1:line.find('}')]
              if append:
                methodBody = methodBody.strip() + '\n' + tab + insertion.strip().replace('\n', '\n' + tab)
              else:
                methodBody = insertion.strip().replace('\n', '\n' + tab) + '\n' + tab + methodBody.strip()
              fout.write('\n' + tab + methodBody.strip() + '\n}')
              # have now written method up to and including the '}'
              fout.write(line[line.find('}')+1:])
              lineNum += 1
              while lineNum < len(lines):
                line = lines[lineNum]
                fout.write(line)
                lineNum += 1
              fout.close()
          os.remove(os.path.join(root, name))
      os.rmdir(controllerDir + self._insertionsDir)
      os.rmdir(controllerDir)

    # Remove temp directory
    # Our portion is now empty, but do a recursive delete in case a previous
    # program execution did not terminate correctly and did not clear out its temp files
    for root, dirs, files in os.walk(self._tempOutputDir, topdown=False):
      for name in files:
        os.remove(os.path.join(root, name))
      for name in dirs:
        os.rmdir(os.path.join(root, name))
    os.rmdir(self._tempOutputDir)

    fout = open(filedir + '/' + 'virtual_pins.txt', 'w+')
    for num, port in enumerate(self._virtualPins):
      fout.write(str(num) + ':   ' + port.getParent().getName() + '.' + port.getName() + '\n')
    fout.close()
    fout = open(filedir + '/' + 'data_map.txt', 'w+')
    for (output, inputs) in self._dataMap.iteritems():
      fout.write('\n' + str(output) + ':\t')
      for input in inputs:
        fout.write(str(input) + '   ')
    fout.close()
    #print res


  def _processCodeFile(self, codeFile, controller, component):
    codeFile = self._codePath(codeFile)
    controllerDir = str(controller).replace('<','(').replace('>',')')
    controllerDir = self._tempOutputDir + controllerDir + '/'
    if controller not in self._controllerDirs:
      self._controllerDirs[controller] = controllerDir
    if not os.path.exists(controllerDir):
      os.mkdir(controllerDir)
    if not os.path.exists(controllerDir + self._methodsDir):
      os.mkdir(controllerDir + self._methodsDir)
    if not os.path.exists(controllerDir + self._insertionsDir):
      os.mkdir(controllerDir + self._insertionsDir)

    res = '\n-- see code file ' + codeFile
    fin = open(codeFile, 'r')
    code = fin.read()
    fin.close()
    if '@@file' in code:
      codeFileBaseName = ntpath.basename(codeFile)
      if '@@filemain' in code:
        fout = open(controllerDir + '__mainCodeFile__' + codeFileBaseName[-4:], 'w+')
        fout.write(code[code.find('\n', code.find('@@filemain')):])
      else:
        fout = open(controllerDir + codeFileBaseName, 'w+')
        fout.write(code[code.find('\n', code.find('@@file')):])
      fout.close()
      return
    # Process any device-specific code tags now, such as virtual pin numbers and device index
    code = self._processLocalTags(component, code)
    # Extract declarations, insertions, and new methods from code file
    newDeclarations = self._getCodeTag(code, 'declare')
    newMethods = self._getCodeTag(code, 'method')
    newInsertions = self._getCodeTag(code, 'insert')
    fin.close()
    # Store declarations, insertions, and new methods (checking for duplicates)
    fout = open(controllerDir + self._declarationsFile, 'a+')
    prevDeclarations = fout.read()
    fout.seek(0)
    fout.write('\n')
    for newDeclaration in newDeclarations:
      res += '\n\tsee new declaration:'
      res += '\n\t\t' + str(newDeclaration)
      for newLine in newDeclaration[1].splitlines(True):
        if newLine not in prevDeclarations:
          fout.write(newLine)
    fout.close()
    for newMethod in newMethods:
      res += '\n\tsee new method:'
      res += '\n\t\t' + str(newMethod)
      if not os.path.exists(controllerDir + self._methodsDir + newMethod[0]):
        fout = open(controllerDir + self._methodsDir + newMethod[0].replace('*', '^') + '.txt', 'w+')
        fout.write(newMethod[1])
        fout.close()
    for newInsertion in newInsertions:
      res += '\n\tsee new insertion:'
      res += '\n\t\t' + str(newInsertion)
      fout = open(controllerDir + self._insertionsDir + newInsertion[0].replace('*', '^') + '.txt', 'a+')
      prevInsertions = fout.read()
      fout.seek(0)
      if newInsertion[1] not in prevInsertions:
        fout.write('\n' + newInsertion[1])
      fout.close()
    #print res

  # Get the component to consider when replacing tags
  # If is a driver, will return its driven component
  # Otherwise will return itself
  def _getDrivenComponent(self, component):
    res = 'getDrivenComponent for ' + str(component)
    try:
      drivenName = component.getParameter('drivenComponent')
      res += '\n\tgot drivenName ' + drivenName
    except (KeyError, AttributeError):
      res += '\nexception'
      #print res
      return component

    classname = str(component)
    classname = classname[classname.rfind('.')+1:]
    classname = classname[0:classname.find(' object')]
    # Find the parent of the device in question
    componentParent = None
    for parent in self._components:
      if (component, classname) in parent.components.values():
        res += '\n\tFound Parent! ' + parent.getName() + ' ' + str(parent)
        componentParent = parent
        break
    if componentParent is None:
      res += '\n\tCould not find parent'
      #print res
      return component

    # Look for driven component within children of the same parent
    for (child, classname) in componentParent.components.values():
      childName = child.getName()
      if '.' in childName:
        childName = childName[childName.rfind('.')+1:]
      if drivenName in childName:
        res += '\n\tFound driven component! ' + child.getName() + ' ' + str(child)
        #print res
        return child

    res += '\n\tCould not find driven component'
    #print res
    return component


  # Process local tags, i.e. ones that can be known incrementally (before design is complete)
  #  such as virtual pin numbers or device indices
  # Some will need to be processed again later at the global stage
  #  Example: @pinNum<arg> tag can't be finished now since the desired pin may not yet have been seen
  #   so this tag will be modified to indicate which device it pertains to, but not resolved to a number yet
  def _processLocalTags(self, device, code):
    for tag in ['@deviceTypeCount', '@deviceTypeIndex']:
      # Make its own type be the default argument
      deviceType = str(device.__class__)
      deviceType = deviceType[deviceType.rfind('.')+1:]
      if '\'>' in deviceType:
        deviceType = deviceType[0:-2]
      code = code.replace(tag, tag + '<' + deviceType + '>')
      code = code.replace(tag + '<' + deviceType + '><', tag + '<')
      # Insert unique device identifier as first argument
      if 'deviceTypeIndex' in tag:
        code = code.replace(tag, tag + str(device))
      else:
        code = code.replace(tag, tag + '<0>')

    for tag in ['@portID', '@pinNum', '@dataOutputID', '@dataInputID', '@dataInputSourceID', '@param']:
      # Make 0 be the default argument
      code = code.replace(tag, tag + '<0>')
      code = code.replace(tag + '<0><', tag + '<')
      # Insert unique device identifier as first argument
      code = code.replace(tag, tag + str(device))

    return code

  def _processTags(self, code):
    tag = '@controllerPins'
    controllerPins = []
    for port in self._virtualPins:
      try:
        pinNum = port.getParameter('controllerPin').getParameter('codeName')
        controllerPins.append(str(pinNum))
      except (KeyError, AttributeError):
        controllerPins.append(str(-1))
    code = code.replace(tag, self._arrayToCppStr(controllerPins))

    for tag in ['@portID', '@pinNum', '@dataOutputID', '@dataInputID', '@dataInputSourceID', '@param']:
      while code.find(tag) >= 0:
        res = ''
        res += '\nreplacing tag ' + tag
        # Extract the relevant device and desired pin from arguments
        tagIndex = code.find(tag)
        firstArgIndex = code.find('<', tagIndex)
        secondArgIndex = code.find('<', firstArgIndex+1)
        firstArg = code[firstArgIndex : secondArgIndex]
        secondArg = code[secondArgIndex : code.find('>', secondArgIndex)+1]
        deviceArg = firstArg
        pinArg = secondArg[1:-1]
        res += '\ndeviceArg <' + deviceArg + '>'
        res += '\npinArg <' + pinArg + '>'
        try:
          pinArg = int(pinArg)
        except ValueError:
          pass

        # Find the desired device
        devices = None
        for testDevice in self._components:
          if str(testDevice) in deviceArg:
            res += '\nsee testDevice' + str(testDevice)
            devices = [self._getDrivenComponent(testDevice)]
            if self._getDrivenComponent(testDevice) is not testDevice:
              devices.append(testDevice)
        # If device isn't found (weird), just replace tag with -1
        if devices is None:
          code = code.replace(tag + firstArg + secondArg, str(-1))
          continue
        res += '\nfound deviceArg devices ' + str(devices)
        for device in devices: # Try both the actual device and the driven device
          if code.find(tag + firstArg + secondArg) < 0:
            break
          res += '\nsee device ' + device.getName() + ' ' + str(device)
          if '@param' in tag:
            try:
              param = device.getParameter(pinArg)
              code = code.replace(tag + firstArg + secondArg, str(param))
            except (KeyError, AttributeError):
              pass
            continue
          # Look through known pins to get desired one and replace with its virtual pin number
          pinIndex = 0
          for pinNum in range(len(self._virtualPins)):
            pin = self._virtualPins[pinNum]
            res += '\nsee pin ' + pin.getParent().getName() + ' .<' + pin.getName() + '>'
            if pin.getParent() is device:
              res += '\n\tcorrect device'
              if 'dataInput' in tag and not isinstance(pin, DataInputPort):
                res += '\n\tskipping, not data input'
                continue
              if 'dataOutput' in tag and not isinstance(pin, DataOutputPort):
                res += '\n\tskipping, not data output'
                continue
              if pinArg == pinIndex or pinArg == pin.getName() or '.' + pinArg in pin.getName():
                res += '\n\tfound pin'
                res += '\nreplacing with virtual pin number ' + str(pinNum)
                if 'pinNum' in tag:
                  # Replace with microcontroller pin number
                  code = code.replace(tag + firstArg + secondArg, str(controllerPins[pinNum]))
                else:
                  # replace with virtual pin number
                  if '@dataInputSourceID' in tag:
                    for (outputID, inputIDs) in self._dataMap.iteritems():
                      if pinNum in inputIDs:
                        code = code.replace(tag + firstArg + secondArg, str(outputID))
                    # If we didn't find it, replace with -1
                    code = code.replace(tag + firstArg + secondArg, str(-1))
                  else:
                    code = code.replace(tag + firstArg + secondArg, str(pinNum))
                break
              pinIndex += 1
        # If we didn't find it, replace with -1
        code = code.replace(tag + firstArg + secondArg, str(-1))
        #print res

    for tag in ['@deviceTypeCount', '@deviceTypeIndex']:
      while code.find(tag) >= 0:
        res = ''
        res += '\nreplacing tag ' + tag
        #res += code
        # Extract the relevant device and desired type from arguments
        tagIndex = code.find(tag)
        firstArgIndex = code.find('<', tagIndex)
        secondArgIndex = code.find('<', firstArgIndex+1)
        firstArg = code[firstArgIndex : secondArgIndex]
        secondArg = code[secondArgIndex : code.find('>', secondArgIndex)+1]
        deviceArg = firstArg
        typeArg = secondArg[1:-1]
        res += '\ndeviceArg <' + deviceArg + '>'
        res += '\ntypeArg <' + typeArg + '>'
        # Find the desired device
        device = None
        for testDevice in self._components:
          if str(testDevice) in deviceArg:
            device = self._getDrivenComponent(testDevice)
        # If device isn't found (weird), just replace tag with -1
        res += '\nfound device arg ' + (device.getName() if device is not None else 'None')

        # Find value of tag and make replacement
        count = 0
        for nextDevice in self._components:
          res += '\n\tsee device ' + nextDevice.getName()
          res += '\tof type ' + str(nextDevice)
          if 'deviceTypeIndex' in tag and self._getDrivenComponent(nextDevice) is device or nextDevice is device:
            break
          nextType = str(nextDevice.__class__)
          nextType = nextType[nextType.rfind('.')+1:]
          if nextType.find(typeArg) == 0:
            res += '\t-\t is correct type'
            count += 1
        res += '\n\ttotal count/index is ' + str(count)
        code = code.replace(tag + firstArg + secondArg, str(count))
        #print res

    tag = '@dataMappings'
    code = code.replace(tag, self._arrayToCppStr(self._dataMap.values(), '-1'))
    tag = '@dataOutputCount'
    code = code.replace(tag, str(len(self._dataMap)))
    tag = '@dataOutDegree'
    if len(self._dataMap) > 0:
      code = code.replace(tag, str(max(map(lambda x:len(self._dataMap.values()[x]), range(len(self._dataMap.values()))))))
    else:
      code = code.replace(tag, str(0))
    tag = '@dataOutputs'
    code = code.replace(tag, self._arrayToCppStr(self._dataMap.keys(), '-1'))

    tag = '@uiDescriptions'
    # Each description is of the form
    # name$type$dataInput0Name,ID,dataInput1Name,ID$dataOutput0Name,ID,dataOutput1Name,ID,...$options
    uiDescriptions = []
    for (component, ports) in self._components.iteritems():
      try:
        name = component.getLabel()
        type = component.getTypeName()
        options = component.getOptionStr()
      except AttributeError:
        continue
      description = 'UI$' + name + '$' + type + '$'
      for port in ports:
        if isinstance(port, DataInputPort):
          description += port.getName() + ','
          description += str(self._virtualPins.index(port)) + ','
      if description[-1] == ',':
        description = description[0:-1]
      description += '$'
      for port in ports:
        if isinstance(port, DataOutputPort):
          description += port.getName() + ','
          description += str(self._virtualPins.index(port)) + ','
      if description[-1] == ',':
        description = description[0:-1]
      description += '$' + options
      uiDescriptions.append('\"' + description + '\"')
    code = code.replace(tag, self._arrayToCppStr(uiDescriptions))

    tag = '@numUIDescriptions'
    code = code.replace(tag, str(len(uiDescriptions)))

    tag = '@uiDataMap'
    # Will be of the form
    # outputID0-inputID0-inputID1-...$outputID1-inputID0-inputID1-...$...$
    uiDataMap = ''
    for (output, inputs) in self._dataMap.iteritems():
      if len(uiDataMap) > 0:
        uiDataMap += '$'
      uiDataMap += str(output)
      for input in inputs:
        uiDataMap += '-' + str(input)
    uiDataMap = '\"MAP$' + uiDataMap + '$\"'
    code = code.replace(tag, uiDataMap)

    tag = '@pinTypes'
    pinTypes = []
    for port in self._virtualPins:
      pinType = str(port.__class__)
      pinType = pinType[pinType.rfind('.')+1:]
      pinType = pinType[0:pinType.find('\'')]
      pinTypes.append('\"' + pinType + '\"')
    code = code.replace(tag, self._arrayToCppStr(pinTypes))

    tag = '@pinProtocols'
    protocols = []
    for port in self._virtualPins:
      try:
        protocols.append('\"' + str(port.getParameter('protocol')) + '\"')
      except KeyError:
        protocols.append('\"direct\"')
    code = code.replace(tag, self._arrayToCppStr(protocols))

    tag = '@numPins'
    code = code.replace(tag, str(len(self._virtualPins)))

    tag = '@autoPoll'
    autoPoll = {}
    for (outputID, inputIDs) in self._dataMap.iteritems():
      autoPoll[outputID] = []
      if len(inputIDs) == 0:
        autoPoll[outputID].append('false')
      for inputID in inputIDs:
        inputPort = self._virtualPins[inputID]
        try:
          autoPoll[outputID].append(str(inputPort.getParameter('autoPoll')).lower())
        except KeyError:
          autoPoll[outputID].append('false')
    code = code.replace(tag, self._arrayToCppStr(autoPoll.values(), 'false'))

    return code



  # Use the given file handle or string to search for the given code tag
  # Will return a list of 2-element tuples
  #   The first element is the line containing the code tag (without the tag itself)
  #   The second element are all lines between the found tag and the next tag
  # If given a file handle, its position will remain unchanged
  def _getCodeTag(self, code, tag):
    if tag.find('@@') < 0:
      tag = '@@' + tag
    res = []
    if isinstance(code, str):
      lines = code.splitlines(True)
    else:
      codePos = code.tell() # will put pos back to starting position when done
      code.seek(0)
      lines = code.readlines()
      code.seek(codePos)

    if len(lines) == 0:
      return res
    nextLine = lines.pop(0)
    while len(lines) > 0:
      while len(lines) > 0 and nextLine.find(tag) < 0:
        nextLine = lines.pop(0)
      if nextLine.find(tag) >= 0:
        tagText = ''
        tagBody = ''
        tagText += nextLine[nextLine.find(tag) + len(tag):]
        tagText = tagText.replace('<','').replace('>', '')
        if len(lines) > 0:
          nextLine = lines.pop(0)
        while nextLine.find('@@') < 0:
          if len(nextLine) > 0 and nextLine[0] == '\n':
            nextLine = nextLine[1:]
          if len(nextLine) > 0 and nextLine[-1] == '\n':
            nextLine = nextLine[0:-1]
          tagBody += '\n' + nextLine
          if len(lines) > 0:
            nextLine = lines.pop(0)
          else:
            break
        res.append((tagText.strip(), tagBody.strip()))
    return res

  def _arrayToCppStr(self, array, fillerVal="\"\"", length=-1):
    if not isinstance(array, (list, tuple)):
      if isinstance(array, str):
        return array
      return str(array)
    res = '{'
    maxLength = 0
    for item in array:
      if isinstance(item, (list, tuple)) and len(item) > maxLength:
        maxLength = len(item)
    length = length if length >= 0 else len(array)
    for i in range(length):
      if i >= len(array):
        res += str(fillerVal)
      else:
        res += self._arrayToCppStr(array[i], fillerVal, maxLength)
      if i < length-1:
        res += ', '

    res += '}'
    return res

  def _codePath(self, codeFile):
    fullFile = codeFile
    if not os.path.exists(codeFile):
      fullFile = os.path.join(SVGGEN_DIR, codeFile)
    if not os.path.exists(fullFile):
      fullFile = os.path.join(SVGGEN_DIR, 'library')
      fullFile = os.path.join(fullFile, codeFile)
    if not os.path.exists(fullFile):
      fullFile = os.path.join(SVGGEN_DIR, 'library/code')
      fullFile = os.path.join(fullFile, codeFile)
    return fullFile