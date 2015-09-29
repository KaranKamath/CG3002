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
	byte i = 0;
	while (1) {
		altitude(&dataRead);
		byte res = xQueueSendToBack(report, &dataRead, 500);
		if (res) {
			i = (i+1)%2;
		}
		if (i==0) {
			digitalWrite(32, HIGH);
		} else {
			digitalWrite(32, LOW);
		}
		gyroreader(&dataRead);
		xQueueSendToBack(report, &dataRead, 500);
		
		accemagno(&dataRead);
		xQueueSendToBack(report, &dataRead, 500);
		
		vTaskDelay(DELAY_IMU);
	}
}
// Pressure Raw is an integer. Is it possible to have Pi deal with converting it to meters/millimeters? Formula available.
void altitude(data_t *psData) {
	psData->id = IDALTI;
	float alti = ps.pressureToAltitudeMeters(ps.readPressureMillibars());
	psData->data[0] = floor(alti*1000+0.5);
}
			

void altitude_init() {
	ps.init();
	ps.enableDefault();
}

void gyroreader (data_t *gyroData) {
	gyro.read();
	gyroData->id = IDGYRO;
	gyroData->data[0] = gyro.g.x;
	gyroData->data[1] = gyro.g.y;
	gyroData->data[2] = gyro.g.z;
}

void gyro_init(void) {
	gyro.init();
	gyro.enableDefault();
}

void accemagno(data_t *accmaData) {
	accmag.read();
	accmaData->id = IDACCMAG;
	accmaData->data[0] = accmag.a.x;
	accmaData->data[1] = accmag.a.y;
	accmaData->data[2] = accmag.a.z;
	accmaData->data[3] = accmag.m.x;
	accmaData->data[4] = accmag.m.y;
	accmaData->data[5] = accmag.m.z;
}

void accemagno_init(void) {
	accmag.init();
	accmag.enableDefault();
}