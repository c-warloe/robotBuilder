@@declare
#include "OneWireSerial.h"
#include "arduino.h"
OneWireSerial bt; 

@@insert<void robotSetup()>
bt = OneWireSerial(@pinNum<TX>, @pinNum<RX>);
bt.begin(9600);
//sendBluetoothData("AT+NAME");
//sendBluetoothData("myRobotBT");

@@insert<bool bluetoothAvailable()>
return bt.available();

@@insert<void sendBluetoothChar(char toSend)>
delay(1);
bt.write(toSend);

@@insert<char getBluetoothChar()>
delay(1);
return (char) bt.read();