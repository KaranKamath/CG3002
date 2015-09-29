#include "ImuFunctions.h"
#include "global.h"
#include "UartComm.h"

LPS ps;
L3G gyro;
LSM303 accmag;

xQueueHandle report;

void setup(void) {
	Wire.begin();
	Serial.begin(9600);
	pinMode(32, OUTPUT);
	pinMode(13, OUTPUT);
	
	altitude_init();
	accemagno_init();
	gyro_init();
	
	report = xQueueCreate(QUEUE_SIZE, sizeof(data_t));
}

int main(void)
{
	
	init();
	setup();
    
	xTaskCreate(altitude, "Altitude", 512, NULL, 2, NULL);
//	xTaskCreate(accemagno, "Acc and Mag", 512, NULL, 1, NULL);
//	xTaskCreate(gyroreader, "Gyroscope", 512, NULL, 2, NULL);
	xTaskCreate(sendData, "Send Data", 1024, NULL, 3, NULL);
	vTaskStartScheduler();
}