#include "ImuFunctions.h"
#include "global.h"
#include "UartComm.h"
#include "Obstacle.h"

LPS ps;
L3G gyro;
LSM303 accmag;

xQueueHandle report;

void setup(void) {
	Serial.begin(9600);
	Wire.begin();
	
	pinMode(32, OUTPUT);
	pinMode(26, OUTPUT);
	pinMode(28, OUTPUT);
	
	altitude_init();
	accemagno_init();
	gyro_init();
	setupObstacle();
	
	report = xQueueCreate(QUEUE_SIZE, sizeof(data_t));
}

int main(void)
{
	
	init();
	setup();
    TaskHandle_t alt, send, ui, motor;
	
	
	xTaskCreate(readDistanceSensors,"UI",STACK_DEPTH,NULL,3,&ui);
	xTaskCreate(imu, "S", 256, NULL, 2, &alt);
	xTaskCreate(sendData, "R", 256, NULL, 2, &send);
	xTaskCreate(driveActuators,"M",STACK_DEPTH,NULL,2,&motor);
	if (ui == NULL ) {
		digitalWrite(26, HIGH);
	}
	
	if (motor == NULL) {
		digitalWrite(28, HIGH);
	}
	
	vTaskStartScheduler();
}

