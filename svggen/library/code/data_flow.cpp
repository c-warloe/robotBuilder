
@@declare
#include "string_functions.h"
#define NUM_DATA_OUTPUTS @dataOutputCount
#define DATA_OUTDEGREE @dataOutDegree
int dataMapping[NUM_DATA_OUTPUTS][DATA_OUTDEGREE] = @dataMappings;
int dataOutputIDs[NUM_DATA_OUTPUTS] = @dataOutputs;
bool autoPoll[NUM_DATA_OUTPUTS][DATA_OUTDEGREE] = @autoPoll;
char outputData[50];
bool validGetData;

@@insert<void robotLoop()>
processData();

@@method<void processData()>
void processData()
{
  for(int dataOutput = 0; dataOutput < NUM_DATA_OUTPUTS; dataOutput++)
  {
    // If any of its inputs are set to autoPolling, get data from it and send to those inputs
    validGetData = false;
    for(int dataInput = 0; dataInput < DATA_OUTDEGREE && dataMapping[dataOutput][dataInput] >= 0; dataInput++)
    {
      if(autoPoll[dataOutput][dataInput])
      {
        if(!validGetData)
          getData(dataOutputIDs[dataOutput]);
        if(validGetData)
          processData(outputData, dataMapping[dataOutput][dataInput]);
      }

    }
  }
}

@@method<char* getData(int sourceID)>
char* getData(int sourceID)
{
  return getData(sourceID, -1);
}

@@method<char* getData(int sourceID, int destID)>
char* getData(int sourceID, int destID)
{
  outputData[0] = '\0';
  validGetData = false;
  return outputData;
}

@@method<void processData(const char* data, int sourceID, int* destIDs, int numDestIDs)>
void processData(const char* data, int sourceID, int* destIDs, int numDestIDs)
{
  for(int i = 0; i < numDestIDs; i++)
  {
    if(destIDs[i] >= 0)
      processData(data, sourceID, destIDs[i]);
  }
}

@@method<void processData(const char* data, int destID)>
void processData(const char* data, int destID)
{
  return processData(data, -1, destID);
}

@@method<void processData(const char* data, int sourceID, int destID)>
void processData(const char* data, int sourceID, int destID)
{
  Serial.print("Finished ProcessData <");
  Serial.print(data);
  Serial.print(">");
  Serial.print(" for ");
  Serial.println(destID);
  Serial.println();
}