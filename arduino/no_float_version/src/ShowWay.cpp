#include "ImuFunctions.h"
#include "global.h"
#include "UartComm.h"
#include "Obstacle.h"
#include "ReadKeypad.h"

//xQueueHandle report;

void setup(void) {
	Serial.begin(9600);
	Wire.begin();
	setupObstacle(); 
	setupUart();
	setupKeypad();
	
	//report = xQueueCreate(QUEUE_SIZE, sizeof(data_t)); 
}

int main(void)
{
	
	init();
	setup();
	
    TaskHandle_t alt, ui;
	
	xTaskCreate(readDistanceSensors, "UI", 350, NULL, 3, &ui);
	xTaskCreate(imu, "S", 500, NULL, 2, &alt);
	//xTaskCreate(sendData, "R", 300, NULL, 2, &send);
	
	if (ui == NULL || alt == NULL ) {
		pinMode(LED_PIN, OUTPUT);
		digitalWrite(LED_PIN, HIGH);
		Serial.println("One or more tasks not created");
	} else {
		Serial.println("Tasks created correctly");
	}
	
	//TODO: test if tasks are created correctly
	vTaskStartScheduler();
}

