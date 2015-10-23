#include "ImuFunctions.h"
#include "global.h"
#include "UartComm.h"
#include "Obstacle.h"
#include "ReadKeypad.h"

LPS ps;
L3G gyro;
LSM303 accmag;

xQueueHandle report;
xSemaphoreHandle flag;

void reset() {
	xSemaphoreGiveFromISR(flag, NULL);
}

void setupReset()
{
	pinMode(RESET_PIN, INPUT_PULLUP);
	vSemaphoreCreateBinary(flag);
	attachInterrupt(digitalPinToInterrupt(RESET_PIN), reset, FALLING);
}


void resetTask(void *p) {
	if (xSemaphoreTake(flag, portMAX_DELAY) == pdTRUE) {
		vTaskSuspendAll();
		setupUart();
		if (!xTaskResumeAll()) {
			taskYIELD();
		}
	}
}

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
//	setupReset();
}

int main(void)
{
	
	init();
	setup();
	
    TaskHandle_t alt, send, ui;
	
	xTaskCreate(readDistanceSensors, "UI", 300, NULL, 3, &ui);
	xTaskCreate(imu, "S", 256, NULL, 2, &alt);
	xTaskCreate(sendData, "R", 300, NULL, 2, &send);
	
//	xTaskCreate(resetTask, "RS", 200, NULL, 2, NULL);
	//TODO: test if tasks are created correctly
	vTaskStartScheduler();
}

