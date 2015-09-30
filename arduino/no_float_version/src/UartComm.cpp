/*
* UartComm.cpp
*
* Created: 27/9/2015 11:02:22 PM
*  Author: Linh
*/

#include "UartComm.h"
#define DELAY_UART 200
#define SIZE_ACK 4
void setupUart() {
	Serial1.begin(9600);
	//while (!handshake());
	handshake();
}

void handshake(){
	
	char ack[10];
	int cntFlag=0;
	memset(ack, 0, sizeof(ack));

	/* Establish Handshake */

	while (cntFlag == 0){
		if (strcmp(ack,"ACK")!= 0) {
			char handshake[10];
			strcpy(handshake, "BEGIN\n");
			Serial1.write(handshake);
			Serial.print("Sent : ");
			Serial.println(handshake);
			delay(200);
			int numRecieved = Serial1.available();
			if(numRecieved > 0){
				Serial1.readBytesUntil(0,ack,3);
			}
			Serial.print("Received : ");
			Serial.println(ack);
			} else {
			//echo ACK
			if (cntFlag == 0) {
				//Serial.write(ack);
				char ackSend[5];
				strcpy(ackSend, "ACK\n");
				Serial1.write(ackSend);
				Serial.print("Sent : ");
				Serial.println(ackSend);
				cntFlag++;
			}
			Serial.println("Count Flag is");
			Serial.println(cntFlag);
		}
	}
	return;
	
}

void sendData(void *p) {
	data_t received;
	char toSend[80];
	char ackData[5];
	while (1) {
		if (xQueueReceive(report, &received, 1000)) {
			do {
				if (received.id == IDGYRO) {
					snprintf(toSend, sizeof(toSend), "%d|%d,%d,%d|%d\n", IDGYRO,received.data[0], received.data[1], received.data[2], 0);
					} else if (received.id == IDALTI) {
					snprintf(toSend, sizeof(toSend), "%d|%d|%d\n", IDALTI,received.data[0], 0);
					} else if (received.id == IDACCMAG) {
					snprintf(toSend, sizeof(toSend), "%d|%d,%d,%d,%d,%d,%d|%d\n", IDACCMAG,received.data[0], received.data[1], received.data[2],received.data[3], received.data[4], received.data[5],0);
				}
				
				//always send new data -- or not, it can be stuck here without doing anything else
				//pretty sure it will have to stop for obstacle task -- though this depends on whether
				//reading from serial can be pre-empted or not
				Serial.write(toSend);
				Serial1.write(toSend);
				vTaskDelay(500);
				int numRecieved = Serial1.available();
				strcpy(ackData, "   ");
				if (numRecieved > 0){
					Serial1.readBytesUntil(0, ackData, 3);
					Serial.println(ackData);
				}
			} while(strcmp(ackData,"ACK")!=0);
		}
	}
}