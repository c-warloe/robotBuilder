
@@declare
#include "arduino.h"
long PWMFrequency[3];

@@insert<void setup()><@prepend>
Serial.begin(9600);
robotSetup();

@@insert<void loop()><@prepend>
robotLoop();

@@insert<void setDO(int pin, bool setHigh)>
digitalWrite(controllerPins[pin], setHigh);

@@insert<void setPWM(int pin, int duty)>
analogWrite(controllerPins[pin], duty);

@@insert<bool readDI(int pin)>
return digitalRead(controllerPins[pin]);

@@insert<int readAI(int pin)>
return analogRead(controllerPins[pin]);

@@insert<void setPinMode(int pin, int mode)>
switch(mode)
{
  case DO: pinMode(pin, OUTPUT); break;
  case DI: pinMode(pin, INPUT); break;
  case AO:
  case PWM: pinMode(pin, OUTPUT); break;
  case SERVO:
    pinMode(pin, OUTPUT);
    switch(pin)
    {
      case 5:
      case 6:
        PWMFrequency[0] = setPWMFrequency(pin, 980); break;
      case 9:
      case 10:
        PWMFrequency[1] = setPWMFrequency(pin, 480); break;
      case 3:
      case 11:
        PWMFrequency[2] = setPWMFrequency(pin, 480); break;
    }
    break;
  case AI: break;
}

@@insert<long getPWMFrequency(int pin)>
switch(controllerPins[pin])
{
  case 5:
  case 6:
    return PWMFrequency[0];
  case 9:
  case 10:
    return PWMFrequency[1];
  case 3:
  case 11:
    return PWMFrequency[2];
}

@@insert<int setPWMFrequency(int pin, long frequency)>
byte mode;
long baseFrequency;
if(pin == 3 || pin == 9 || pin == 10 || pin == 11)
    baseFrequency = 31250;
if(pin == 5 || pin == 6)
    baseFrequency = 62500;
long error = baseFrequency;
int divisor = 1;
if(pin == 5 || pin == 6 || pin == 9 || pin == 10)
{
  int divisors[] = {1,8,64,256,1024};
  for(int i = 0; i < 5; i++)
  {
    long newError = frequency - baseFrequency / divisors[i];
    newError *= newError < 0 ? -1 : 1;
    if(newError < error)
    {
      error = newError;
      divisor = divisors[i];
    }
  }
  Serial.print("divisor: "); Serial.println(divisor);
  Serial.print("frequency: "); Serial.println(baseFrequency / divisor);
  Serial.print("error: "); Serial.println(error);
  switch(divisor)
  {
    case 1: mode = 0x01; break;
    case 8: mode = 0x02; break;
    case 64: mode = 0x03; break;
    case 256: mode = 0x04; break;
    case 1024: mode = 0x05; break;
    default: return -1;
  }
  if(pin == 5 || pin == 6)
    TCCR0B = TCCR0B & 0b11111000 | mode;
  else
    TCCR1B = TCCR1B & 0b11111000 | mode;
}
else if(pin == 3 || pin == 11)
{
  int divisors[] = {1,8,32,64,128,256,1024};
  for(int i = 0; i < 7; i++)
  {
    long newError = frequency - baseFrequency / divisors[i];
    newError *= newError < 0 ? -1 : 1;
    if(newError < error)
    {
      error = newError;
      divisor = divisors[i];
    }
  }
  switch(divisor)
  {
    case 1: mode = 0x01; break;
    case 8: mode = 0x02; break;
    case 32: mode = 0x03; break;
    case 64: mode = 0x04; break;
    case 128: mode = 0x05; break;
    case 256: mode = 0x06; break;
    case 1024: mode = 0x7; break;
    default: return -1;
  }
  TCCR2B = TCCR2B & 0b11111000 | mode;
}
return baseFrequency / divisor;