/*
 * ImuFunctions.cpp
 *
 * Created: 27/9/2015 10:54:40 AM
 *  Author: Linh
 */ 

#include "ImuFunctions.h"
#include "debugging.h"
#include "global.h"

xSemaphoreHandle i2c_bus = 0;

void imu(void *p) {
	data_t dataRead;
	while (1) {
		dataRead.id = IDIMU;
		altitude(&dataRead);
		gyroreader(&dataRead);
		accemagno(&dataRead);
		xQueueSendToBack(report, &dataRead, 500);
		//to test if the queue is full
		//xQueueSendToBack(report, &dataRead, portMAX_DELAY);
		vTaskDelay(DELAY_IMU);
	}
}

void altitude(data_t *psData) {
	float alti = ps.pressureToAltitudeMeters(ps.readPressureMillibars());
	psData->data[0] = floor(alti*1000+0.5);
}

void altitude_init() {
	ps.init();
	ps.enableDefault();
}

void gyroreader (data_t *gyroData) {
	gyro.read();
	gyroData->data[OFFSETGY+0] = gyro.g.x;
	gyroData->data[OFFSETGY+1] = gyro.g.y;
	gyroData->data[OFFSETGY+2] = gyro.g.z;
}

void gyro_init(void) {
	gyro.init();
	gyro.enableDefault();
}

void accemagno(data_t *accmaData) {
	accmag.read();
	accmaData->data[OFFSETAM+0] = accmag.a.x;
	accmaData->data[OFFSETAM+1] = accmag.a.y;
	accmaData->data[OFFSETAM+2] = accmag.a.z;
	accmaData->data[OFFSETAM+3] = accmag.m.x;
	accmaData->data[OFFSETAM+4] = accmag.m.y;
	accmaData->data[OFFSETAM+5] = accmag.m.z;
}

void accemagno_init(void) {
	accmag.init();
	accmag.enableDefault();
}