
@@declare
#define numLineDetectors @deviceTypeCount
int lineDetectorPins[numLineDetectors];
int lineDetectorThresholds[numLineDetectors];

@@insert<void robotSetup()>
setDO(@portID<ledSignal>, 1);
lineDetectorPins[@deviceTypeIndex] = @portID<sensorSignal>;
lineDetectorThresholds[@deviceTypeIndex] = 500;
calibrateLineDetector(@deviceTypeIndex);

@@insert<char* getData(int sourceID, int destID)><@prepend>
if(sourceID == @dataOutputID<curValue>)
{
  itoa(readLineDetectorValue(@deviceTypeIndex), outputData, 10);
  validGetData = true;
  return outputData;
}
if(sourceID == @dataOutputID<seeLine>)
{
  itoa(seeLine(@deviceTypeIndex), outputData, 10);
  validGetData = true;
  return outputData;
}

@@method<int readLineDetectorValue(int detector)>
int readLineDetectorValue(int detector)
{
  return readAI(lineDetectorPins[detector]);
}

@@method<bool seeLine(int detector)>
bool seeLine(int detector)
{
  return readLineDetectorValue(detector) > lineDetectorThresholds[detector];
}

@@method<void calibrateLineDetector()>
void calibrateLineDetector(int detector)
{
  setDO(@portID<ledSignal>, 1);
  delay(3000);
  int min = readLineDetectorValue(detector);
  setDO(@portID<ledSignal>, 0);
  delay(500);
  setDO(@portID<ledSignal>, 1);
  delay(3000);
  int max = readLineDetectorValue(detector);
  lineDetectorThresholds[detector] = (max+min)/2;
  setDO(@portID<ledSignal>, 0);
  delay(500);
  setDO(@portID<ledSignal>, 1);
  delay(50);
}