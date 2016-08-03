import os
from svggen import SVGGEN_DIR
from svggen.api.DataComponent import DataComponent
from svggen.api.composables.CodeComposable import CodeComposable

class CodeComponent(DataComponent):
  def define(self):
    DataComponent.define(self)
    self.addParameter('controller')
    self._codeFiles = []
    self._code = []

  def assemble(self):
    DataComponent.assemble(self)
    code = CodeComposable()
    self.composables['code'] = code

  def addCodeFile(self, codeFiles):
    if not isinstance(codeFiles, (list, tuple)):
      codeFiles = [codeFiles]
    for file in codeFiles:
      if file not in self._codeFiles:
        fullFile = os.path.join(SVGGEN_DIR, file)
        if not os.path.exists(fullFile):
          fullFile = os.path.join(SVGGEN_DIR, 'library')
          fullFile = os.path.join(fullFile, file)
        if not os.path.exists(fullFile):
          fullFile = os.path.join(SVGGEN_DIR, 'library/code')
          fullFile = os.path.join(fullFile, file)
        if not os.path.exists(fullFile):
          raise ValueError('Code file %s does not exist (added by %s)' % (file, self.getName()))
        self._codeFiles.append(fullFile)

  def addCodeFolder(self, codeFolder):
    if not isinstance(codeFolder, str):
      return
    foldername = codeFolder.strip()
    while foldername[len(foldername)-1] == '/':
      foldername = foldername[0:len(foldername)-1]
    while foldername[len(foldername)-1] == '\\':
      foldername = foldername[0:len(foldername)-1]

    for root, dirs, files in os.walk(foldername, topdown=False):
      for name in files:
        self.addCodeFile(foldername + '/' + name)

  def getCodeFiles(self):
    return self._codeFiles[:]

  def addCode(self, code):
    if not isinstance(code, (list, tuple)):
      code = [code]
    for codeString in code:
      if codeString not in self._code:
        self._code.append(codeString)

  def getCode(self):
    return self._code[:]

  def getParameter(self, name, strict=True):
    return DataComponent.getParameter(self, name)

if __name__ == '__main__':
  CodeComponent()
