
#include "global.h"
#include "ReadKeypad.h"

xSemaphoreHandle sem;
void setupKeypad(void) {
	pinMode(2, INPUT_PULLUP);
	attachInterrupt(digitalPinToInterrupt(2), key_isr, FALLING);
	vSemaphoreCreateBinary(sem);
}

void key_isr(void) {
	xSemaphoreGiveFromISR(sem, NULL);
} 

void read_keypad(void *p) {
	while (1) {
		if (xSemaphoreTake(sem, portMAX_DELAY) == pdTRUE) {
			vTaskSuspendAll();
			detachInterrupt(digitalPinToInterrupt(2));
			Serial.println("#123456#");
			delay(1000);
			if (digitalRead(2) == LOW) {
				Serial.println("Pressed again");	
			}
			attachInterrupt(digitalPinToInterrupt(2), key_isr, FALLING);
			if (!xTaskResumeAll()) {
				taskYIELD();
			}
		}
	}
}

