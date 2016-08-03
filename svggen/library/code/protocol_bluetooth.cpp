
@@declare
#include "string_functions.h"
char bluetoothData[50];
bool bluetoothConnected;
#define dataCommand "DATA"
#define dataRequest "GET"
#define uiRequest "UI_DESCRIPTION"
char* UI_DESCRIPTIONS[] = @uiDescriptions;
bool validBluetoothData;

@@method<bool bluetoothAvailable()>
bool bluetoothAvailable()
{
}

@@method<void sendBluetoothChar(char toSend)>
void sendBluetoothChar(char toSend)
{
}

@@method<char getBluetoothChar()>
char getBluetoothChar()
{
}

@@insert<void robotSetup()>
bluetoothConnected = false;
validBluetoothData = false;
bluetoothData[0] = '\0';

@@insert<void robotLoop()>
processBluetoothData();

@@insert<char* getData(int sourceID, int destID)><@prepend>
if(equalsIgnoreCase(protocol[sourceID], "bluetooth"))
{
  // TODO control frequency of polling in a way that is fair to all polled inputs
  // and that also does not limit frequency of incoming requests

  // Request data from bluetooth
  // use format GET$outputPortID$inputPortID
  char toSend[50]; toSend[0] = '\0';
  strcpy(dataRequest, toSend, 50);
  concat(toSend, "$", toSend, 50);
  concatInt(toSend, sourceID, toSend, 50);
  concat(toSend, "$", toSend, 50);
  sendBluetoothData(toSend);
  // For now, pretend like it was an invalid getData
  // When the bluetooth controller responds with DATA command, it will be processed then
  outputData[0] = '\0';
  validGetData = false;
  return outputData;
}

@@insert<void processData(const char* data, int sourceID, int destID)><@prepend>
if(equalsIgnoreCase(protocol[destID], "bluetooth"))
{
  // TODO control frequency of polling in a way that is fair to all polled inputs
  // and that also does not limit frequency of incoming requests

  // Send data to bluetooth
  // use format DATA$data$outputPortID$inputPortID
  char toSend[50]; toSend[0] = '\0';
  strcpy(dataCommand, toSend, 50);
  concat(toSend, "$", toSend, 50);
  concat(toSend, data, toSend, 50);
  concat(toSend, "$", toSend, 50);
  concatInt(toSend, sourceID, toSend, 50);
  concat(toSend, "$", toSend, 50);
  concatInt(toSend, destID, toSend, 50);
  sendBluetoothData(toSend);
}

@@method<bool getBluetoothData()>
bool getBluetoothData()
{
  if(!bluetoothAvailable())
    return false;
  if(validBluetoothData)
  {
    bluetoothData[0] = '\0';
    validBluetoothData = false;
  }
  int index = length(bluetoothData);
  while(bluetoothAvailable() && !validBluetoothData)
  {
    bluetoothData[index++] = getBluetoothChar();
    validBluetoothData = (bluetoothData[index-1] == '\0');
  }
  if(validBluetoothData)
  {
    // If it is a heartbeat, respond to it now
    if(equals(bluetoothData, "?"))
    {
      sendBluetoothData("?");
      bluetoothData[0] = '\0';
      validBluetoothData = false;
      return false;
    }
    Serial.print("Got BT data <"); Serial.print(bluetoothData); Serial.println(">");
  }
  return validBluetoothData;
}
//bool getBluetoothData()
//{
//  bluetoothData[0] = '\0';
//  if(!bluetoothAvailable())
//    return false;
//  int timeout = 50;
//  int index = 0;
//  bool terminated = false;
//  unsigned long start = millis();
//  while(!terminated && millis() - start < timeout)
//  {
//    while(!bluetoothAvailable() && millis() - start < timeout);
//    bluetoothData[index++] = getBluetoothChar();
//    start = millis();
//    terminated = (bluetoothData[index-1] == '\0');
//  }
//  if(index > 0 && bluetoothData[index-1] != '\0')
//    bluetoothData[index] = '\0';
//  // If it is a heartbeat, respond to it now
//  if(equals(bluetoothData, "?"))
//  {
//    sendBluetoothData("?");
//    bluetoothData[0] = '\0';
//    return false;
//  }
//  Serial.print("Got BT data <"); Serial.print(bluetoothData); Serial.println(">");
//  return true;
//}

@@method<void sendBluetoothData(const char* data)>
void sendBluetoothData(const char* data)
{
  int index = 0;
  for(; index < length(data); index++)
    sendBluetoothChar(data[index]);
  if(data[index-1] != '\0')
    sendBluetoothChar('\0');
  Serial.print("Sent BT data <"); Serial.print(data); Serial.println(">");
}

@@method<void processBluetoothData()>
void processBluetoothData()
{
  if(!getBluetoothData())
    return;
  if(indexOf(bluetoothData, uiRequest) >= 0)
  {
    for(int i = 0; i < @numUIDescriptions; i++)
      sendBluetoothData(UI_DESCRIPTIONS[i]);
    sendBluetoothData(@uiDataMap);
    return;
  }
  // Parse data
  bool isRequest = false;
  char data[10];  data[0] = '\0';
  if(indexOf(bluetoothData, dataCommand) >= 0)
    isRequest = false;
  else if(indexOf(bluetoothData, dataRequest) >= 0)
    isRequest = true;
  else
    return;
  bluetoothConnected = true;
  char outputIDChar[3]; outputIDChar[0] = '\0';
  char inputIDChar[3]; inputIDChar[0] = '\0';
  int index = 0;
  int btLength = length(bluetoothData);
  for(; index < btLength && bluetoothData[index] != '$'; index++);
  index++; // get passed first dollar sign
  if(!isRequest)
  {
    int dataIndex = 0;
    while(index < btLength && bluetoothData[index] != '$')
      data[dataIndex++] = bluetoothData[index++];
    data[dataIndex] = '\0';
    index++; // get passed second dollar sign
  }
  int idIndex = 0;
  while(index < btLength && bluetoothData[index] != '$')
    outputIDChar[idIndex++] = bluetoothData[index++];
  outputIDChar[idIndex] = '\0';
  index++;
  idIndex = 0;
  while(index < btLength && bluetoothData[index] != '$')
    inputIDChar[idIndex++] = bluetoothData[index++];
  inputIDChar[idIndex] = '\0';

  int outputID = length(outputIDChar) > 0 ? atoi(outputIDChar) : -1;
  int inputID = length(inputIDChar) > 0 ? atoi(inputIDChar) : -1;

  Serial.print("\tgot data <"); Serial.print(data); Serial.println(">");
  Serial.print("\tgot output <"); Serial.print(outputIDChar); Serial.print("> -> "); Serial.println(outputID);
  Serial.print("\tgot input <"); Serial.print(inputIDChar); Serial.print("> -> "); Serial.println(inputID);

  if(isRequest)
  {
    getData(outputID);
    if(validGetData)
    {
      char toSend[50]; toSend[0] = '\0';
      strcpy(dataCommand, toSend, 50);
      concat(toSend, "$", toSend, 50);
      concat(toSend, outputData, toSend, 50);
      concat(toSend, "$", toSend, 50);
      concatInt(toSend, outputID, toSend, 50);
      concat(toSend, "$", toSend, 50);
      concat(toSend, inputIDChar, toSend, 50);
      sendBluetoothData(toSend);
    }
  }
  else
  {
    if(inputID >= 0 && outputID < 0)
      processData(data, inputID);
    else if(inputID >= 0 && outputID >= 0)
      processData(data, outputID, inputID);
    else if(outputID >= 0)
    {
      // Find index in array of this output ID
      for(int i = 0; i < NUM_DATA_OUTPUTS; i++)
      {
        if(dataOutputIDs[i] == outputID)
          processData(data, outputID, dataMapping[i], DATA_OUTDEGREE);
      }
    }
  }
}

@@method<bool isBluetoothConnected()>
bool isBluetoothConnected()
{
  return bluetoothConnected;
}