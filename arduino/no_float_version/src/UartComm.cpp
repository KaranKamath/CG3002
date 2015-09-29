/*
 * UartComm.cpp
 *
 * Created: 27/9/2015 11:02:22 PM
 *  Author: Linh
 */ 

#include "UartComm.h"
#define DELAY_UART 200
#define SIZE_ACK 3
void setupUart() {
	Serial1.begin(9600);
	while (!handshake());
}

boolean handshake(void) {
	char ack[SIZE_ACK];
	Serial1.write("BEGIN\n");
	delay(DELAY_UART);
	//TODO: check if this delay is still necessary
	if (Serial1.available()) {
		Serial1.readBytesUntil(0, ack, SIZE_ACK);
	}
	//to test
	Serial.println(ack);
	if (strcmp(ack, "ACK") == 0) {
		Serial1.write("ACK\n");
		return true;
	}
	return false;
}

void sendData(void *p) {
	data_t received;
	char toSend[80];
	char ack[SIZE_ACK];
	while (1) {
		if (xQueueReceive(report, &received, 1000)) {
			if (received.id == IDGYRO) {
				snprintf(toSend, sizeof(toSend), "%d|%d,%d,%d|%d\n", IDGYRO, 
				received.data[0], received.data[1], received.data[2], 0);
			} else if (received.id == IDALTI) {
				snprintf(toSend, sizeof(toSend), "%d|%d|%d\n", IDALTI, 
				received.data[0], 0);
			} else if (received.id == IDACCMAG) {
				snprintf(toSend, sizeof(toSend), "%d|%d,%d,%d,%d,%d,%d|%d\n", IDACCMAG,
				received.data[0], received.data[1], received.data[2],
				received.data[3], received.data[4], received.data[5],
				0);
			} 
			
			//always send new data -- or not, it can be stuck here without doing anything else
			//pretty sure it will have to stop for obstacle task -- though this depends on whether 
			//reading from serial can be pre-empted or not
			Serial.print(toSend);
			while (strcmp(ack, "ACK") != 0) {
				Serial1.write(toSend);
				if (Serial1.available()) {
					Serial1.readBytesUntil(0, ack, SIZE_ACK);
					//to check
					Serial.println(ack);
				}
			}
		} 
	}
}