
@@declare
#define numDistanceSensors @deviceTypeCount
int distanceSensorPins[numDistanceSensors];
int distanceSensorThresholds[numDistanceSensors];

@@insert<void robotSetup()>
distanceSensorPins[@deviceTypeIndex] = @portID<signal>;
distanceSensorThresholds[@deviceTypeIndex] = 512;

@@method<int readDistanceSensor(int sensorIndex)>
int readDistanceSensor(int sensorIndex)
{
  Serial.print("Reading distance sensor "); Serial.println(sensorIndex);
  return readAI(distanceSensorPins[sensorIndex]);
}

@@method<bool threshDistanceSensor(int sensorIndex)>
bool threshDistanceSensor(int sensorIndex)
{
  Serial.print("Thresholding distance sensor "); Serial.println(sensorIndex);
  return readAI(distanceSensorPins[sensorIndex]) > distanceSensorThresholds[sensorIndex];
}

@@insert<char* getData(int sourceID, int destID)><@prepend>
if(sourceID == @dataOutputID)
{
  itoa(readDistanceSensor(@deviceTypeIndex), outputData, 10);
  validGetData = true;
  return outputData;
}
