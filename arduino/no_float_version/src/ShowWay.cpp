#include "ImuFunctions.h"
#include "global.h"
#include "UartComm.h"

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
	
	report = xQueueCreate(QUEUE_SIZE, sizeof(data_t));
}

int main(void)
{
	
	init();
	setup();
    TaskHandle_t alt, send;
	xTaskCreate(imu, "S", 512, NULL, 2, &alt);
	xTaskCreate(sendData, "R", 512, NULL, 1, &send);

	vTaskStartScheduler();
}

