
@@declare
#define numLEDs @deviceTypeCount
int ledPins[numLEDs];

@@insert<void robotSetup()>
ledPins[@deviceTypeIndex] = @portID<signal>;
setLED(@deviceTypeIndex, 0);

@@method<void setLED(int ledIndex, int brightness)>
void setLED(int ledIndex, int brightness)
{
  setPWM(ledPins[ledIndex], brightness);
  Serial.print("Set analog LED "); Serial.print(ledIndex);
  Serial.print(" to "); Serial.println(brightness);
}

@@insert<void processData(const char* data, int sourceID, int destID)><@prepend>
if(destID == @dataInputID)
{
  int duty = (int) atof(data);
  setLED(@deviceTypeIndex, duty);
}