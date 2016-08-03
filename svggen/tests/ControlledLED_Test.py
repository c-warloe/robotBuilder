from svggen.api.component import Component
from svggen.library.Arduino import ArduinoProMini

__author__ = 'Joseph'

def test_make_controlledLED(display=False):
  c = Component()
  c.setName='uiTest'
  controller = ArduinoProMini()

  c.addSubcomponent('myLed', 'ControlledLED', inherit=True)
  c.setParameter('myLed.label', 'myLED')
  c.setParameter('myLed.controllerPin', 13)
  c.setParameter('myLed.controller', controller)
  #c.setParameter('myLed.type', 'digital')
  c.setParameter('myLed.led.autoPoll', False)
  c.setParameter('myLed.toggle.autoPoll', False)

  # Add bluetooth module
  # TODO get this added automatically somehow
  c.addSubcomponent('bt', 'BluetoothModule', inherit=True)
  c.setParameter('bt.controller', controller)
  c.setParameter('bt.TX.controllerPin', 11)
  c.setParameter('bt.RX.controllerPin', 10)

  #print 'tester sees parameters ', c.parameters


  # Make output
  c.makeOutput("output/controlledLED", display = display)

if __name__ == '__main__':
  test_make_controlledLED(display=True)
