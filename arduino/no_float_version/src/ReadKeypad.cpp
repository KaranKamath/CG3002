
#include "global.h"
#include "ReadKeypad.h"

xSemaphoreHandle flag;

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
	flag = xSemaphoreCreateBinary();
	keypad.setDebounceTime(100);
	pinMode(27, OUTPUT);
	digitalWrite(27, LOW);
	pinMode(2, INPUT_PULLUP);

	attachInterrupt(digitalPinToInterrupt(2), keyIsr, FALLING);
}

void keyIsr(void) {
	xSemaphoreGiveFromISR(flag, NULL);
} 

void readKeypad(void *p) {
	while (1) {
		if (xSemaphoreTake(flag, portMAX_DELAY) == pdTRUE) {
			vTaskSuspendAll();
			detachInterrupt(digitalPinToInterrupt(2));
			pinMode(27, INPUT);
			Serial.println("#123456#");
			char key;
			byte len = 0;
			char keydata[20];
			while (1) {
				key = keypad.getKey();			
				if (key != NO_KEY) {
					keydata[len] = key;
					len++;
					Serial.println(key);
					//TODO: check for overflow
					if (key == '#' && len == 1) {
						continue;
					} else if (key == '1') {
						keydata[len] = '\n';
						len++;
						keydata[len] = '\0';
						len++;
						Serial.println(keydata);
						break;
					}				
				}
			}
			pinMode(27, OUTPUT);
			digitalWrite(27, LOW);

			attachInterrupt(digitalPinToInterrupt(2), keyIsr, FALLING);
			
			if (!xTaskResumeAll()) {
				taskYIELD();
			}			
		}
	}
}

