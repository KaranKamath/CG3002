
 #import <String.h>

 char ack[50];
 int cntFlag;
 char ackData[50];
 
 void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial1.begin(9600);
  strcpy(ack, "");
  cntFlag=0;
  strcpy(ackData, "");
}

void loop() {
  if(strcmp(ack,"ACK")!=0){
    char handshake[50];
    strcpy(handshake, "BEGIN\n");
    Serial1.write(handshake);
    delay(200);
    int numRecieved = Serial1.available();
    if(numRecieved>0){
      Serial1.readBytesUntil(0,ack,numRecieved);
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
  }
    if(cntFlag==1){
      if(strcmp(ackData,"ACK")!=0){    
      char sensorData[50];
      strcpy(sensorData, "0|32|45|23|1\n");  
      Serial1.write(sensorData);
      delay(200);
        int numRecieved = Serial1.available();
        if(numRecieved>0){
          Serial1.readBytesUntil(0,ackData,numRecieved);
        }  
      }
    }  
}


