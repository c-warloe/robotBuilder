
@@declare
#define numLEDs @deviceTypeCount
int ledPins[numLEDs];

@@insert<void robotSetup()>
ledPins[@deviceTypeIndex] = @portID<signal>;
turnOffLED(@deviceTypeIndex);

@@method<void turnOnLED(int ledIndex)>
void turnOnLED(int ledIndex)
{
  setDO(ledPins[ledIndex], 1);
  Serial.print("Set digital LED "); Serial.print(ledIndex);
  Serial.print(" to "); Serial.println(1);
}

@@method<void turnOffLED(int ledIndex)>
void turnOffLED(int ledIndex)
{
  setDO(ledPins[ledIndex], 0);
  Serial.print("Set digital LED "); Serial.print(ledIndex);
  Serial.print(" to "); Serial.println(0);
}

@@insert<void processData(const char* data, int sourceID, int destID)><@prepend>
if(destID == @dataInputID)
{
  int value = (int) atof(data);
  if(value)
    turnOnLED(@deviceTypeIndex);
  else
    turnOffLED(@deviceTypeIndex);
}