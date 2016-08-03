
@@declare
#define numServos @deviceTypeCount
int servoPins[numServos];

@@insert<void robotSetup()>
servoPins[@deviceTypeIndex] = @portID<signal>;
setAngle(@deviceTypeIndex, 0);

@@method<bool setAngle(int servoNum, int angle)>
bool setAngle(int servoNum, int angle) 
{
  setPWM(servoPins[servoNum], angleToDuty(angle, servoPins[servoNum]));
  Serial.print("Set servo ");
  Serial.print(servoNum);
  Serial.print(" to angle "); Serial.println(angle);
  return true;
}

@@insert<void processData(const char* data, int sourceID, int destID)><@prepend>
if(destID == @dataInputID)
{
  int angle = (int) atof(data);
  setAngle(@deviceTypeIndex, angle);
}

@@method<int angleToDuty(double angle, int pin)>
int angleToDuty(double angle, int pin)
{
  double pwmPeriod = 1000.0/(double)getPWMFrequency(pin);
  double pulseWidth = angle/180.0 * (1.2 - 0.3) + 0.3;
  return pulseWidth / pwmPeriod * 255;
}













