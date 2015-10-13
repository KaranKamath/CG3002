
#include "global.h"
#include "ReadKeypad.h"
#define SIZE_ACK 3

const byte ROWS = 4;
const byte COLS = 3;
char keys[ROWS][COLS] = {
	{'1','2','3'},
	{'4','5','6'},
	{'7','8','9'},
	{'*','0','#'}
};
byte rowPins[ROWS] = {22, 23, 24, 2};
byte colPins[COLS] = {25, 26, 27};

Keypad keypad = Keypad( makeKeymap(keys), rowPins, colPins, ROWS, COLS );
//NOTE: Update file WInterrupts.c
//NOTE: If the ending and starting key is on the same row (i.e get the reading from the same pin)
//then the interrupt will be triggered again upon exit (even though the flag is already cleared in
//updated WInterrupts.c file and the interrupt is already disabled when the button is pressed).
void setupKeypad(void) {
	keypad.setDebounceTime(100);
}

void readKeypad(void) {
	char key;
	int splCount=0;
	byte len = 0;
	char keydata[40];
	char sendData[42];
	char ack[SIZE_ACK+2];
	while (1) {
		key = keypad.getKey();
		if (key != NO_KEY) {
			if(key!='#' && key!='*'){
				keydata[len] = key;
				len++;
				Serial.println(key);
				//TODO: check for overflow
				} else if ((key == '#' || key == '*') && len == 0) {
				continue;
				}else if ((key == '#'|| key == '*') && splCount == 0){
				splCount++;
				keydata[len] = '*';
				len++;
				Serial.println("*");
				continue;
				} else if ((key == '#'|| key == '*') && splCount ==1){
				keydata[len] = '\n';
				len++;
				keydata[len] = '\0';
				len++;
				Serial.println(keydata);
				break;
			}
		}
	}
	
	snprintf(sendData, sizeof(sendData), "%s",keydata);
	strcpy(ack, "   ");
	while (strcmp(ack, "ACK") != 0) {
		Serial.write(sendData);
		Serial1.write(sendData);
		delay(1000);
		if (Serial1.available()) {
			Serial1.readBytesUntil(0, ack, SIZE_ACK);
			ack[SIZE_ACK] = '\0';
		}
	}
	Serial.println(ack);
}

