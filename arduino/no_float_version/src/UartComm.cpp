/*
 * UartComm.cpp
 *
 * Created: 27/9/2015 11:02:22 PM
 *  Author: Linh
 */ 

#include "UartComm.h"

void setupUart() {
	Serial1.begin(9600);
}

void sendData(void *p) {
	data_t received;
	char toSend[80];
	byte i = 0;
	while (1) {
		if (i== 0) {
			digitalWrite(26, LOW);
		}
		else {
			digitalWrite(26, HIGH);
		}
		if (xQueueReceive(report, &received, 1000)) {
			i = (i+1)%2;
			
			if (received.id == IDGYRO) {
				snprintf(toSend, sizeof(toSend), "%d|%d,%d,%d|%d\n", IDGYRO, received.data[0], received.data[1], received.data[2], 0);
			} else if (received.id == IDALTI) {
				snprintf(toSend, sizeof(toSend), "%d|%d|%d\n", IDALTI, received.data[0], 0);
			} else if (received.id == IDACCMAG) {
				snprintf(toSend, sizeof(toSend), "%d|%d,%d,%d,%d,%d,%d|%d\n", IDACCMAG,
				received.data[0], received.data[1], received.data[2],
				received.data[3], received.data[4], received.data[5],
				0);
			} else {
				digitalWrite(13, LOW);
			}
			Serial.print(toSend);
		} else {
			digitalWrite(28, HIGH);
		}
	}
}