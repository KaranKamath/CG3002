/*
 * ImuFunctions.cpp
 *
 * Created: 27/9/2015 10:54:40 AM
 *  Author: Linh
 */ 

#include "ImuFunctions.h"
#include "debugging.h"
#include "global.h"

void imu(void *p) {
	data_t data_down;
	data_t data_up;
	data_down.id = IDDOWN;
	data_up.id = IDUP;
	
	L3G gyro_down;
	LPS ps_down;
	LSM303 accma_down;
	
	L3G gyro_up;
	LPS ps_up;
	LSM303 accma_up;
	
	gyro_down = gyro_init(L3G::sa0_high);
	ps_down = altitude_init(LPS::sa0_high);
	accma_down = accemagno_init(LSM303::sa0_high);
	
	gyro_up = gyro_init(L3G::sa0_low);
	ps_up = altitude_init(LPS::sa0_low);
	accma_up = accemagno_init(LSM303::sa0_low);
	
	while (1) {	
		altitude(ps_down, &data_down);
		gyroreader(gyro_down, &data_down);
		accemagno(accma_down, &data_down); 
		
		altitude(ps_up, &data_up);
		gyroreader(gyro_up, &data_up);
		accemagno(accma_up, &data_up);
		
		xQueueSendToBack(report, &data_down, 500);
		xQueueSendToBack(report, &data_up, 500);

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
LPS altitude_init(LPS::sa0State addr) {
	LPS ps;
	if (!ps.init(LPS::device_auto, addr)) {
		while (1);
	}
	ps.enableDefault();
	return ps;
}

void gyroreader (L3G gyro, data_t *gyroData) {
	gyro.read();
	gyroData->data[OFFSETGY+0] = gyro.g.x;
	gyroData->data[OFFSETGY+1] = gyro.g.y;
	gyroData->data[OFFSETGY+2] = gyro.g.z;
}

L3G gyro_init(L3G::sa0State addr) {
	L3G gyro;
	gyro.init(L3G::device_auto, addr);
	gyro.enableDefault();
	return gyro;
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

LSM303 accemagno_init(LSM303::sa0State addr) {
	LSM303 accmag;
	accmag.init(LSM303::device_auto, addr);
	accmag.enableDefault();
	return accmag;
}

