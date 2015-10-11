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
	setupKeypad();
	setupUart();
	report = xQueueCreate(QUEUE_SIZE, sizeof(data_t)); 
	//TODO: test if the queue is created correctly
	//TODO: change to pointer to save RAM? Data are overwritten 
	
}

int main(void)
{
	
	init();
	setup();
	
    TaskHandle_t alt, send, ui, motor, key;
	
	xTaskCreate(readDistanceSensors, "UI", 200, NULL, 3, &ui);
	xTaskCreate(imu, "S", 200, NULL, 2, &alt);
	xTaskCreate(sendData, "R", 300, NULL, 2, &send);
	//xTaskCreate(driveActuators,"M", configMINIMAL_STACK_SIZE, NULL, 2, &motor);
	
	
	//TODO: test if tasks are created correctly
	vTaskStartScheduler();
}

