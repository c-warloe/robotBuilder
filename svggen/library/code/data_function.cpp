
@@insert<char* getData(int sourceID, int destID)><@prepend>
if(sourceID == @dataOutputID)
{
  int input = (int) atof(getData(@dataInputSourceID));
  if(!validGetData)
  {
    outputData[0] = '\0';
    return outputData;
  }
  validGetData = true;
  itoa((int) (@param<function>), outputData, 10);
  return outputData;
}

@@insert<void processData(const char* data, int sourceID, int destID)><@prepend>
if(destID == @dataInputID)
{
  int input = (int) atof(data);
  char outputData[10];
  itoa((int) (@param<function>), outputData, 10);
  for(int dataOutput = 0; dataOutput < NUM_DATA_OUTPUTS; dataOutput++)
  {
    if(dataOutputIDs[dataOutput] == @dataOutputID)
      processData(outputData, dataOutput, dataMapping[dataOutput], DATA_OUTDEGREE);
  }
}