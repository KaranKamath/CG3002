/*
 * UartComm.cpp
 *
 * Created: 27/9/2015 11:02:22 PM
 *  Author: Linh
 */ 

#include "UartComm.h"
#include "ReadKeypad.h"

#define DELAY_UART 50
#define BAUD_RATE 9600
#define SIZE_ACK 3

void setupUart() {
	Serial1.begin(BAUD_RATE);
//	handshake();
}

void handshake(void) {
	char ack[SIZE_ACK + 2];
	while (strcmp(ack, "ACK") != 0) {
		Serial.write("BEGIN\n");
		delay(DELAY_UART);
		if (Serial.available()) {
			Serial.readBytesUntil(0, ack, SIZE_ACK);
			ack[SIZE_ACK] = '\0';
		}
	}

	Serial.println(ack);
	Serial1.write("ACK\n");
}

void sendData(void *p) {
	data_t received;
	char toSend[100];
	while (1) {
		if (xQueueReceive(report, &received, portMAX_DELAY)) {
			if (received.id == IDDOWN || received.id == IDUP) {
				snprintf(toSend, sizeof(toSend), "%d|%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n", received.id, 
				received.data[0], 		
				received.data[0+OFFSETAM], received.data[1+OFFSETAM], received.data[2+OFFSETAM],
				received.data[3+OFFSETAM], received.data[4+OFFSETAM], received.data[5+OFFSETAM],
				received.data[0+OFFSETGY], received.data[1+OFFSETGY], received.data[2+OFFSETGY]);
			} else if (received.id == IDOBSTACLE) {
				snprintf(toSend, sizeof(toSend), "%d|%d,%d,%d,%d,%d\n", IDOBSTACLE,
				received.data[0], received.data[1], received.data[2], received.data[3], received.data[4]);
			}
			
			Serial.print(toSend);
//			Serial1.write(toSend);
		} 
	}
}