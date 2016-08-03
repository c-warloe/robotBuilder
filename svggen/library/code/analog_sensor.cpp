
@@declare
#define numAnalogSensors @deviceTypeCount
int analogSensorPins[numAnalogSensors];

@@insert<void robotSetup()>
analogSensorPins[@deviceTypeIndex] = @portID<signal>;

@@method<int readAnalogSensor(int sensorIndex)>
int readAnalogSensor(int sensorIndex)
{
  Serial.print("Reading analog sensor "); Serial.println(sensorIndex);
  return readAI(analogSensorPins[sensorIndex]);
}

@@insert<char* getData(int sourceID, int destID)><@prepend>
if(sourceID == @dataOutputID)
{
  itoa(readAnalogSensor(@deviceTypeIndex), outputData, 10);
  validGetData = true;
  return outputData;
}
