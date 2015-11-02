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
	data_t data_down;
	data_t data_up;
	data_down.id = IDDOWN;
	data_up.id = IDUP;
	LPS ps;
	L3G gyro;
	LSM303 accmag;
	altitude_init(ps, LPS::sa0_high);
	gyro_init(gyro, L3G::sa0_high);
	accemagno_init(accmag, LSM303::sa0_high);
	while (1) {	
		altitude(ps, &data_down);
		gyroreader(gyro, &data_down);
		accemagno(accmag, &data_down); 
		xQueueSendToBack(report, &data_down, 500);
		//to test if the queue is full
		//xQueueSendToBack(report, &dataRead, portMAX_DELAY);
		vTaskDelay(DELAY_IMU);
	}
}

void altitude(LPS ps, data_t *psData) {
	float alti = ps.pressureToAltitudeMeters(ps.readPressureMillibars());
	psData->data[0] = floor(alti*1000+0.5);
}

//TODO: Add some way to tell if init fails.
void altitude_init(LPS ps, LPS::sa0State addr) {
	if (!ps.init(LPS::device_auto, addr)) {
		while (1);
	}
	ps.enableDefault();
}

void gyroreader (L3G gyro, data_t *gyroData) {
	gyro.read();
	gyroData->data[OFFSETGY+0] = gyro.g.x;
	gyroData->data[OFFSETGY+1] = gyro.g.y;
	gyroData->data[OFFSETGY+2] = gyro.g.z;
}

void gyro_init(L3G gyro, L3G::sa0State addr) {
	gyro.init(L3G::device_auto, addr);
	gyro.enableDefault();
}

void accemagno(LSM303 accmag, data_t *accmaData) {
	accmag.read();
	accmaData->data[OFFSETAM+0] = accmag.a.x;
	accmaData->data[OFFSETAM+1] = accmag.a.y;
	accmaData->data[OFFSETAM+2] = accmag.a.z;
	accmaData->data[OFFSETAM+3] = accmag.m.x;
	accmaData->data[OFFSETAM+4] = accmag.m.y;
	accmaData->data[OFFSETAM+5] = accmag.m.z;
}

void accemagno_init(LSM303 accmag, LSM303::sa0State addr) {
	accmag.init(LSM303::device_auto, addr);
	accmag.enableDefault();
}

