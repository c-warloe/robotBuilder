
@@declare
#include "string_functions.h"
#define DO 0
#define DI 1
#define AO 2
#define AI 3
#define PWM 4
#define SERVO 5
#define numPins @numPins
int controllerPins[] = @controllerPins;
const char* pinTypes[] = @pinTypes;
const char* protocol[] = @pinProtocols;

@@method<void robotSetup()>
void robotSetup()
{
  // Set each pin to the correct mode
  for(int pinIndex = 0; pinIndex < numPins; pinIndex++)
  {
    if(controllerPins[pinIndex] >= 0 && getPinType(pinIndex) >= 0)
      setPinMode(controllerPins[pinIndex], getPinMateType(pinIndex));
  }
}

@@method<int getPinType(int pin)>
int getPinType(int pin)
{
  if(contains(pinTypes[pin], "DigitalOutput"))
    return DO;
  else if(contains(pinTypes[pin], "DigitalInput"))
    return DI;
  else if(contains(pinTypes[pin], "PWMOutput"))
    return PWM;
  else if(contains(pinTypes[pin], "AnalogOutput"))
    return AO;
  else if(contains(pinTypes[pin], "AnalogInput"))
    return AI;
  else if(contains(pinTypes[pin], "Servo"))
    return SERVO;
  return -1;
}

@@method<int getPinMateType(int pin)>
int getPinMateType(int pin)
{
  if(contains(pinTypes[pin], "DigitalOutput"))
    return DI;
  else if(contains(pinTypes[pin], "DigitalInput"))
    return DO;
  else if(contains(pinTypes[pin], "PWMOutput"))
    return DI;
  else if(contains(pinTypes[pin], "AnalogOutput"))
    return AI;
  else if(contains(pinTypes[pin], "AnalogInput"))
    return PWM;
  else if(contains(pinTypes[pin], "ServoInput"))
    return SERVO;
  return -1;
}

@@method<void robotLoop()>
void robotLoop()
{
}

@@method<void setPinMode(int pin, int mode)>
void setPinMode(int pin, int mode)
{
}

@@method<void setDO(int pin, bool setHigh)>
void setDO(int pin, bool setHigh)
{
}

@@method<void set(int pin)>
void set(int pin)
{
  setDO(pin, 1);
}

@@method<void clear(int pin)>
void clear(int pin)
{
  setDO(pin, 0);
}

@@method<void setPWM(int pin, int duty)>
void setPWM(int pin, int duty)
{
}

@@method<int setPWMFrequency(int pin, long frequency)>
// Set the PWM Frequency for the given pin
// Will return the frequency achieved, or -1 if arguments are invalid
int setPWMFrequency(int pin, long frequency)
{
}

@@method<long getPWMFrequency(int pin)>
long getPWMFrequency(int pin)
{
}

@@method<bool readDI(int pin)>
bool readDI(int pin)
{
}

@@method<int readAI(int pin)>
int readAI(int pin)
{
}

@@method<bool readAI(int pin, int threshold)>
bool readAI(int pin, int threshold)
{
  return readAI(pin) > threshold;
}