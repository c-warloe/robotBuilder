from svggen.library import getComponent
from svggen.library.Arduino import ArduinoProMini

__author__ = 'Joseph'

def test_make_led(display=False):
  led = getComponent("LED")

  # Define free parameters
  print 'tester sees free parameters ', led.parameters
  led.setParameter('controller', ArduinoProMini())
  led.setParameter('type', 'analog')
  led.setParameter('controllerPin', 13)

  # Make output
  led.makeOutput("output/LED", display = display)

if __name__ == '__main__':
  test_make_led(display=True)