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

// Pressure Raw is an integer. Is it possible to have Pi deal with converting it to meters/millimeters? Formula available.
void altitude(void *p) {
	byte i= 0;
	para_ps_t *myP = (para_ps_t *)p;
	data_t psData;
	psData.id = IDALTI;
	while (1) {
		if (xSemaphoreTake(i2c_bus, 1000)) {
			float alti = myP->ps.pressureToAltitudeMeters(myP->ps.readPressureMillibars());
//			psData->data[0] = floor(alti*1000+0.5);
//			psData->data[0] = 0;
			if (i == 0) {
				digitalWrite(32, HIGH);
			} else {
				digitalWrite(32, LOW);
			}
			byte res = xQueueSendToBack(myP->queue, &psData, 500);
			if (res) {
				i = (i+1)%2;
			} else {
				i = (i-1)%2;
			}
			Serial.println(i);
			xSemaphoreGive(i2c_bus);
		} else {
			digitalWrite(13, HIGH);
		}
		vTaskDelay(500);
	}
}

void accemagno (void *p) {
	data_t *amData = new data_t;
	amData->id = IDGYRO;
	while (1) {
		if (xSemaphoreTake(i2c_bus, 1000)) {
			amData->data[0] = gyro.g.x;
			amData->data[1] = gyro.g.y;
			amData->data[2] = gyro.g.z;
			xQueueSendToBack(report, amData, 500);
			xSemaphoreGive(i2c_bus);
		}
		vTaskDelay(500);
	}
}

void accemagno_init(void) {
	gyro.init();
	gyro.enableDefault();
}

