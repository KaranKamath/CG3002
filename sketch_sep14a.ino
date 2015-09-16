#include <Wire.h>
#include <LPS.h>
#include <Keypad.h>
#include <LSM303.h>
#include <L3G.h>
#include <NewPing.h>

#define TRIGGER_PIN 12
#define ECHO_PIN 11
#define MAX_DISTANCE 200
#import <String.h>

char ack[50];
int cntFlag;
char ackData[50];
int sequence;
LPS ps;
LSM303 compass;
L3G gyro;
NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);

const byte IDALTI = 0;
const byte IDCOMP = 1;
const byte IDGYRO = 2;
const byte IDULTRA = 3;

const byte ROWS = 4; //four rows
const byte COLS = 3; //three columns
char keys[ROWS][COLS] = {
        {'1','2','3'},
        {'4','5','6'},
        {'7','8','9'},
        {'*','0','#'}
        };
byte rowPins[ROWS] = {5, 4, 3, 2}; //connect to the row pinouts of the keypad
byte colPins[COLS] = {8, 7, 6}; //connect to the column pinouts of the keypad


Keypad keypad = Keypad( makeKeymap(keys), rowPins, colPins, ROWS, COLS );
char report[80];
char reportAlti[20];
char reportGyro[40];
char reportUltra[20];

boolean _readAlti = true;
boolean _readComp = true;
boolean _readGyro = true; 
boolean _readUltra = true;

int interval = 100;

void setup()
{
  Serial.begin(9600);
  Serial1.begin(115200);
  
  Wire.begin();
  sequence = 0;
  if (!ps.init() || !gyro.init())
  {
    Serial.println("Failed to autodetect sensor!");
    while (1);
  }

  ps.enableDefault();
  keypad.addEventListener(keypadEvent);
  compass.init();
  compass.enableDefault();
  gyro.enableDefault();
  strcpy(ack, "");
  cntFlag = 0;
  strcpy(ackData, "");
  while (cntFlag == 0)
    handshake();
}

void loop()
{  
  char key = keypad.getKey();
  if (_readAlti) {
    readAlti();
  }
  if (_readComp) {
    readComp();
  }
  if (_readGyro) {
    readGyro();
  }
  if(_readUltra) {
    readUltra();
  }
  sendReport();
}

//NOTE: format of the data sent: can RPi read Ae-3 format
void readAlti() {
    float pressure = ps.readPressureMillibars();
    float altitude = ps.pressureToAltitudeMeters(pressure);
    snprintf(reportAlti, sizeof(reportAlti), "%d|%d|%d\n", IDALTI, int(altitude*1000), 
    (++sequence)%1024);

    Serial.println(reportAlti);
    Serial.println(altitude);
}
void readComp() {
    compass.read();

    snprintf(report, sizeof(report), "%d|%6d, %6d, %6d, %6d, %6d, %6d|%d\n",
    IDCOMP,
    compass.a.x, compass.a.y, compass.a.z,
    compass.m.x, compass.m.y, compass.m.z,
    (++sequence)%1024);
    Serial.println(report);

}
void readGyro() {
    gyro.read();

    snprintf(reportGyro, sizeof(report), "%d|%d, %d, %d|%d\n", IDGYRO, 
    gyro.g.x, gyro.g.y, gyro.g.z, (++sequence)%1024);
    Serial.println(reportGyro);
    Serial.print("G ");
    Serial.print("X: ");
    Serial.print(gyro.g.x);
    Serial.print(" Y: ");
    Serial.print((int)gyro.g.y);
    Serial.print(" Z: ");
    Serial.println((int)gyro.g.z);
}

void keypadEvent(KeypadEvent key) {
  switch (keypad.getState()){
    case PRESSED:
      switch (key){
        case '1': _readAlti = not _readAlti; break;
        case '2': _readComp = not _readComp; break;
        case '3': _readGyro = not _readGyro; break;
        case '4': _readUltra = not _readUltra; break;
        case '*': interval = 1000; break;
        case '#': interval = 100; break;
        default : Serial.println("read key");
        break;
      }
    break;
  }
}
void readUltra() {
  unsigned int uS = sonar.ping();
  snprintf(reportUltra, sizeof(reportUltra), "%d|%d|%d\n", IDULTRA, uS/US_ROUNDTRIP_CM,
  (++sequence)%1024);
  Serial.println(uS/US_ROUNDTRIP_CM);
  Serial.println(reportUltra);
}
void sendReport() {
    boolean _read = true;
    if(cntFlag==1){
      do {
        strcpy(ackData, "");    
      if (_readAlti)
        Serial1.write(reportAlti);
      if (_readComp)
      Serial1.write(report);
      if (_readUltra)
        Serial1.write(reportUltra);
      if (_readGyro) {
        Serial1.write(reportGyro);
      }
      delay(100);
      _read = _readAlti || _readComp || _readUltra || _readGyro;
      int numRecieved = Serial1.available();
      if(numRecieved>0){
          Serial1.readBytesUntil(0,ackData,3);
          Serial.println(ackData);
      }  
     }while(strcmp(ackData,"ACK")!=0 and _read);
   }  
}

void handshake() {
  if(strcmp(ack,"ACK")!=0){
    char handshake[50];
    strcpy(handshake, "BEGIN\n");
    Serial1.write(handshake);
    delay(200);
    int numRecieved = Serial1.available();
    if(numRecieved>0){
      Serial1.readBytesUntil(0,ack,3);
    }
    Serial.write(ack);    
  }else{
    //echo ACK
    if(cntFlag==0){
       Serial.write(ack);
       char ackSend[50];
       strcpy(ackSend, "ACK\n");      
       Serial1.write(ackSend);
       cntFlag++;
    }
    Serial.println("cnt Flag is");
    Serial.println(cntFlag);
  }
}


