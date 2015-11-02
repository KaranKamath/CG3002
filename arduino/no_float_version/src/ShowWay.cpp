#include "ImuFunctions.h"
#include "global.h"
#include "UartComm.h"
#include "Obstacle.h"
#include "ReadKeypad.h"

LPS ps;
L3G gyro;
LSM303 accmag;

xQueueHandle report;

void setup(void) {
	Serial.begin(9600);
	Wire.begin();
	altitude_init();
	accemagno_init();
	gyro_init();
	setupObstacle(); 
	setupUart();
	setupKeypad();
	
	report = xQueueCreate(QUEUE_SIZE, sizeof(data_t)); 
}

int main(void)
{
	
	init();
	setup();
	
    TaskHandle_t alt, send, ui;
	
	xTaskCreate(readDistanceSensors, "UI", 300, NULL, 3, &ui);
	xTaskCreate(imu, "S", 256, NULL, 2, &alt);
	xTaskCreate(sendData, "R", 300, NULL, 2, &send);
	
	if (ui == NULL || alt == NULL || send == NULL) {
		pinMode(LED_PIN, OUTPUT);
		digitalWrite(LED_PIN, HIGH);
	}
	//TODO: test if tasks are created correctly
	vTaskStartScheduler();
}

