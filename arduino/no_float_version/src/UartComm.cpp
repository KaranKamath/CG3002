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
	while (1) {
		if (xQueueReceive(report, &received, 1000)) {
			if (received.id == IDGYRO) {
				snprintf(toSend, sizeof(toSend), "%d|%d,%d,%d|%d\n", IDGYRO, received.data[0], received.data[1], received.data[2], 0);
				Serial.print(toSend);
			} else if (received.id == IDALTI) {
				Serial.println("OK");
			}
		}
	}
}