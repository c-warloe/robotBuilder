
@@declare
#include <EEPROM.h>
#define numServos @deviceTypeCount
int servoPins[numServos];
int servoOffsets[numServos];

@@insert<void robotSetup()>
servoPins[@deviceTypeIndex] = @portID<signal>;
getServoOffsets();
//calibrateServo(@deviceTypeIndex);
setSpeed(@deviceTypeIndex, 0);

@@method<bool setSpeed(int servoNum, int speed)>
bool setSpeed(int servoNum, int speed)
{
  if(speed <= 5 && speed >= -5)
    speed = 0;
  if(speed == 0)
    setPWM(servoPins[servoNum], 0);
  else
    setPWM(servoPins[servoNum], speedToDuty(speed + servoOffsets[servoNum], servoPins[servoNum]));
  Serial.print("Set servo ");
  Serial.print(servoNum);
  Serial.print(" to speed  "); Serial.println(speed);
  return true;
}

@@insert<void processData(const char* data, int sourceID, int destID)><@prepend>
if(destID == @dataInputID)
{
  int speed = (int) atof(data);
  setSpeed(@deviceTypeIndex, speed);
}

@@method<void calibrateServo(int servoNum)>
void calibrateServo(int servoNum)
{
  getServoOffsets();
  int eepromAddress = 0;
  char input = 'x';
  Serial.begin(9600);
  Serial.println("----------------------------");
  Serial.println("Send \'+\' or \'.\' to increase the calibration value");
  Serial.println("Send \'-\' or \',\' to decrease the calibration value");
  Serial.println("Send \'s\' to save the calibration value");
  Serial.println("----------------------------");
  Serial.print("Calibrating servo "); Serial.println(servoNum);
  while(input != 's')
  {
    Serial.print("\tCalibration value: "); Serial.println(servoOffsets[servoNum]);
    setPWM(servoPins[servoNum], speedToDuty(0 + servoOffsets[servoNum], servoPins[servoNum]));
    while(!Serial.available()) {}
    input = Serial.read();
    switch(input)
    {
      case '+':
      case '.': servoOffsets[servoNum]++; break;
      case '-':
      case ',': servoOffsets[servoNum]--; break;
      case 's': eepromWriteInt(2*servoNum, servoOffsets[servoNum]); break;
    }
  }
  Serial.println("----------------------------");
  Serial.println("Calibration complete!");
  delay(1500);
}

@@method<void getServoOffsets()>
void getServoOffsets()
{
  for(int i = 0; i < numServos; i++)
  {
    servoOffsets[i] = eepromReadInt(2*i);
    if(servoOffsets[i] > 90 || servoOffsets[i] < -90)
      servoOffsets[i] = 0;
  }
}

@@method<void eepromWriteInt(int address, int value)>
void eepromWriteInt(int address, int value)
{
  union u_tag
  {
    byte b[2];        //assumes 2 bytes in an int
    int INTtime;
  }
  time;
  time.INTtime=value;

  EEPROM.write(address  , time.b[0]);
  EEPROM.write(address+1, time.b[1]);
}

@@method<int eepromReadInt(int address)>
int eepromReadInt(int address)
{
  union u_tag
  {
    byte b[2];
    int INTtime;
  }
  time;
  time.b[0] = EEPROM.read(address);
  time.b[1] = EEPROM.read(address+1);
  return time.INTtime;
}

@@method<int speedToDuty(double speed, int pin)>
int speedToDuty(double speed, int pin)
{
  double pwmPeriod = 1000.0/(double)getPWMFrequency(pin);
  double pulseWidth = (speed+100)/200.0 * (1.2 - 0.3) + 0.3;
  return pulseWidth / pwmPeriod * 255;
}