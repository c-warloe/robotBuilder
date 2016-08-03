from svggen.library import getComponent
from svggen.library.Arduino import ArduinoProMini

__author__ = 'Joseph'

def test_make_servo(display=False):
  servo = getComponent("EServo")

  # Define free parameters
  #print 'tester sees free parameters ', servo.parameters
  servo.setParameter('controller', ArduinoProMini())
  servo.setParameter('motionType', 'continuous')
  servo.setParameter('controllerPin', 6)

  # Make output
  servo.makeOutput("output/EServo", display = display)

if __name__ == '__main__':
  test_make_servo(display=True)