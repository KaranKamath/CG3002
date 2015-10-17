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
void stub(int i, data_t* dataRead) {
	if (i == 0) {
		int j = 0;
		for (j = 0; j < 9; j++) {
			dataRead->data[j] = j;
		}
		} else {
		int j = 0;
		for (j = 0; j < 9; j++) {
			dataRead->data[j] = 9-j;
		}
	}
}
void imu(void *p) {
	data_t dataRead;
	dataRead.id = IDIMU;
	byte i = 0;
	while (1) {	
		altitude(&dataRead);
		gyroreader(&dataRead);
		accemagno(&dataRead); 
//		stub(i, &dataRead);
//		i = (i+1)%2;
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

//TODO: Add some way to tell if init fails.
void altitude_init() {
	if (!ps.init()) {
		while (1);
	}
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