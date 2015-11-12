#include "ImuFunctions.h"
#include "global.h"
#include "UartComm.h"
#include "Obstacle.h"
#include "ReadKeypad.h"

void setup(void) {
	Serial.begin(9600);
	Wire.begin();
	setupObstacle(); 
	setupUart();
	setupKeypad();
}

int main(void)
{
	
	init();
	setup();
	
    TaskHandle_t alt, ui;
	
	xTaskCreate(readDistanceSensors, "UI", 330, NULL, 3, &ui);
	xTaskCreate(imu, "S", 670, NULL, 2, &alt);
		
	//TODO: test if tasks are created correctly
	vTaskStartScheduler();
}

