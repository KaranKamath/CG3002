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

#define PROXPIN 15

char ack[50];
int cntFlag;
char ackData[50];
int sequence;
LPS ps;
LSM303 compass;
L3G gyro;
NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);
float proxVal, proxMm;

const byte IDALTI = 0;
const byte IDCOMP = 1;
const byte IDGYRO = 2;
const byte IDULTRA = 3;
const byte IDPROX = 4;

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
int motorPins[8] = {42, 43, 44, 45, 46, 47, 48};
byte motorStates[4] = {0, 0, 0, 0};

Keypad keypad = Keypad( makeKeymap(keys), rowPins, colPins, ROWS, COLS );
char report[80];
char reportAlti[20];
char reportGyro[40];
char reportUltra[20];
char reportProx[20];
char keypadresult[50];

boolean _readAlti = false;
boolean _readComp = false;
boolean _readGyro = false; 
boolean _readUltra = false;
boolean _readKeypad = false;
boolean _readProx = false;
boolean _connectUart = false;

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
  memset(ack, 0, sizeof(ack));
  cntFlag = 0;
  memset(ackData, 0, sizeof(ackData));
  while (cntFlag == 0 and _connectUart)
    handshake();
  memset(keypadresult, 0, sizeof(keypadresult));
  setupMotor();
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
  if (_readProx) {
    readProx();
  }
  if (_connectUart) {
    sendReport();
  }
}

void setupMotor() {
  int i = 0;
  for (i = 0; i < 8; i++) 
    pinMode(motorPins[i], OUTPUT);
}

void readAlti() {
    float pressure = ps.readPressureMillibars();
    float altitude = ps.pressureToAltitudeMeters(pressure);
    if (_connectUart)
      sequence = (sequence++)%1024;
    snprintf(reportAlti, sizeof(reportAlti), "%d|%d|%d\n", IDALTI, int(altitude*1000), 
    sequence);

    Serial.println(reportAlti);
    Serial.println(altitude);
}
void readComp() {
    compass.read();
    if (_connectUart)
      sequence = (sequence++)%1024;
    snprintf(report, sizeof(report), "%d|%6d, %6d, %6d, %6d, %6d, %6d|%d\n",
    IDCOMP,
    compass.a.x, compass.a.y, compass.a.z,
    compass.m.x, compass.m.y, compass.m.z,
    sequence);
    Serial.println(report);

}
void readGyro() {
    gyro.read();
    if (_connectUart)
      sequence = (sequence++)%1024;
    snprintf(reportGyro, sizeof(report), "%d|%d, %d, %d|%d\n", IDGYRO, 
    gyro.g.x, gyro.g.y, gyro.g.z, sequence);
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
    if (!_readKeypad) {
      switch (key){
        case '1': _readAlti = not _readAlti; break;
        case '2': _readComp = not _readComp; break;
        case '3': _readGyro = not _readGyro; break;
        case '4': _readUltra = not _readUltra; break;
        case '6': _readProx = not _readProx; break;
        case '7': case '8': runMotor(key - '7'); break;
        case '*': restartUart(); break;
        case '#': _readKeypad = true; break;
        case '9': _connectUart = not _connectUart; Serial.println("In UART\n"); break;
        default : Serial.println("undefined function");
        break;
      }
    } else {
      readKeypad(key);
    }
    break;
  }
}
void readUltra() {
  unsigned int uS = sonar.ping();
  if (_connectUart)
      sequence = (sequence++)%1024;
  snprintf(reportUltra, sizeof(reportUltra), "%d|%d|%d\n", IDULTRA, uS/US_ROUNDTRIP_CM,
  sequence);
  Serial.println(uS/US_ROUNDTRIP_CM);
  Serial.println(reportUltra);
}

void sendReport() {
      do {
        memset(ackData, 0, sizeof(ackData));    
      if (_readAlti)
        Serial1.write(reportAlti);
      if (_readComp)
      Serial1.write(report);
      if (_readUltra)
        Serial1.write(reportUltra);
      if (_readGyro) {
        Serial1.write(reportGyro);
      }
      if (_readProx) {
        Serial1.write(reportProx);
      }
      delay(100);
      
      int numRecieved = Serial1.available();
      if (numRecieved > 0){
          Serial1.readBytesUntil(0, ackData, 3);
          Serial.println(ackData);
      }  
     } while(strcmp(ackData,"ACK")!=0 and _connectUart);  
}

void handshake() {
  if (strcmp(ack,"ACK")!= 0) {
    char handshake[10];
    strcpy(handshake, "BEGIN\n");
    Serial1.write(handshake);
    delay(200);
    int numRecieved = Serial1.available();
    if(numRecieved > 0){
      Serial1.readBytesUntil(0,ack,3);
    }
    Serial.write(ack);    
  } else {
    //echo ACK
    if (cntFlag == 0) {
       Serial.write(ack);
       char ackSend[5];
       strcpy(ackSend, "ACK\n");      
       Serial1.write(ackSend);
       cntFlag++;
    }
    Serial.println("cnt Flag is");
    Serial.println(cntFlag);
  }
}

void restartUart() {
  memset(ack, 0, sizeof(ack));
  cntFlag = 0;
  while (cntFlag == 0 and _connectUart) {
    handshake();
  }
}

void readKeypad(char key) {
  int len = strlen(keypadresult);    
  keypadresult[len] = key;
  Serial.println(len);
  if (key == '#') {  
    
    Serial.println(keypadresult);
    _readKeypad = false;  
    if (_connectUart) {
      len++;
      keypadresult[len] = '\n';
      Serial1.write(keypadresult);
    }
    memset(keypadresult, 0, sizeof(keypadresult));
  }
}

void runMotor(int id) {
  if (motorStates[id] == 0) {
    digitalWrite(motorPins[id*2], 0);
    digitalWrite(motorPins[id*2+1], 1);
    motorStates[id] = 1;
  } else {
    digitalWrite(motorPins[id*2], 1);
    digitalWrite(motorPins[id*2+1], 1);
    motorStates[id] = 0;
  }  
}

void readProx() {
  proxVal = analogRead(PROXPIN);
  proxMm = 106500.8 * pow(proxVal,-0.935) - 10;
  if (_connectUart) 
    sequence = (sequence++)%1024;
  Serial.println(proxMm);
  snprintf(reportProx, sizeof(reportProx), "%d|%d|%d", IDPROX, 
  proxMm, sequence);
  Serial.println(reportProx);
}



