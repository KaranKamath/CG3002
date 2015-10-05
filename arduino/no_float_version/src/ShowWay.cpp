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
	
	pinMode(32, OUTPUT);
	pinMode(26, OUTPUT);
	pinMode(28, OUTPUT);
	
	altitude_init();
	accemagno_init();
	gyro_init();
	setupObstacle();
	setupUart();
	report = xQueueCreate(QUEUE_SIZE, sizeof(data_t)); 
	//TODO: test if the queue is created correctly
	//TODO: change to pointer to save RAM? Data are overwritten 
	setupKeypad();
}

int main(void)
{
	
	init();
	setup();
	
    TaskHandle_t alt, send, ui, motor, key;
	
	xTaskCreate(readDistanceSensors,"UI",STACK_DEPTH,NULL,3,&ui);
	xTaskCreate(imu, "S", 205, NULL, 2, &alt);
	xTaskCreate(sendData, "R", 205, NULL, 2, &send);
	xTaskCreate(read_keypad, "K", STACK_DEPTH, NULL, 4, &key);
	xTaskCreate(driveActuators,"M",205,NULL,2,&motor);
	
	
	//TODO: test if tasks are created correctly
	vTaskStartScheduler();
}

