
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
void setupKeypad(void) {
	keypad.setDebounceTime(100);
}

void readKeypad(void) {
	char key;
	byte splCount = 0;
	byte len = 0;
	char keydata[40];
	char ack [SIZE_ACK+2];
	
	while (1) {
		key = keypad.getKey();			
		if (key != NO_KEY) {
			keydata[len] = key;
			len++;
			Serial.println(key);
			//TODO: check for overflow
			if (key != '#' && key != '*') {
				keydata[len] = key;
				len++;
				Serial.println(key);
			} else if ((key == '#' || key == '*') && len == 0) {
				continue;
			} else if ((key == '#' || key == '*') && splCount == 0) {
				keydata[len] = '*';
				len++;
				splCount++;
				Serial.println('*');
			} else if ((key == '#' || key == '*') && splCount == 1) {
				keydata[len] = '\n';
				len++;
				keydata[len] = '\0';
				len++;
				Serial.println(keydata);
				break;				
			}
		}	
	}
	
	while (strcmp(ack, "ACK") != 0) {
		Serial1.write(keydata);
		//delay or busy wait loop here
		//delay(200);
		//while (!Serial1.available());
		if (Serial1.available()) {
			Serial1.readBytesUntil(0, ack, SIZE_ACK);
			ack[SIZE_ACK] = '\0';
		}
	}
}

