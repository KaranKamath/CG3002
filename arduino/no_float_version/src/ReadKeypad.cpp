
#include "global.h"
#include "ReadKeypad.h"
#define SIZE_ACK 3
#define NUM_STAR 3
#define DELAY_KEYPAD 500
#define DEBOUNCE_TIME 100

const byte ROWS = 4; 
const byte COLS = 3; 
char keys[ROWS][COLS] = {
	{'1','2','3'},
	{'4','5','6'},
	{'7','8','9'},
	{'*','0','#'}
};
byte rowPins[ROWS] = {22, 24, 26, 28}; 
byte colPins[COLS] = {30, 32, 34};

Keypad keypad = Keypad( makeKeymap(keys), rowPins, colPins, ROWS, COLS ); 
void setupKeypad(void) {
	keypad.setDebounceTime(DEBOUNCE_TIME);
}

void readKeypad(void) {
	char key;
	byte splCount = 0;
	byte len = 0;
	char keydata[40];
	char ack [SIZE_ACK+2];
/*	
	while (1) {
		key = keypad.getKey();			
		if (key != NO_KEY) {
			//TODO: check for overflow
			if (key != '#' && key != '*') {
				keydata[len] = key;
				len++;
				Serial.println(key);
			} else if ((key == '#' || key == '*') && len == 0) {
				continue;
			} else if ((key == '#' || key == '*') && splCount != NUM_STAR) {
				keydata[len] = '*';
				len++;
				splCount++;
				Serial.println('*');
			} else if ((key == '#' || key == '*') && splCount == NUM_STAR) {
				keydata[len] = '\n';
				len++;
				keydata[len] = '\0';
				len++;
				Serial.println(keydata);
				break;				
			}
		}	
	}
*/	
	strcpy(keydata, "1*2*1*10\n");
	Serial.println(keydata);
	strcpy(ack, "   ");
	while (strcmp(ack, "ACK") != 0) {
		Serial1.write(keydata);
		delay(DELAY_KEYPAD);
		if (Serial1.available()) {
			Serial1.readBytesUntil(0, ack, SIZE_ACK);
			ack[SIZE_ACK] = '\0';
		}
	}
}

