/*
 * ImuFunctions.h
 *
 * Created: 27/9/2015 10:54:59 AM
 *  Author: Linh
 */ 


#ifndef IMUFUNCTIONS_H_
#define IMUFUNCTIONS_H_

#include "global.h"

#include "LPS.h"
#include "L3G.h"
#include "LSM303.h"

extern LPS ps;
extern L3G gyro;
extern LSM303 accmag;
extern xQueueHandle report;

void imu(void *p);	
void altitude(data_t *psData);
void altitude_init();
void gyroreader(data_t *gyroData);
void gyro_init(void);
void accemagno(data_t *accmaData);
void accemagno_init(void);

#endif /* IMUFUNCTIONS_H_ */