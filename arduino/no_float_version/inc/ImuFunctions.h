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

//extern xQueueHandle report;

void imu(void *p);	
void createString(char *toSend, data_t *psData);
void altitude(LPS ps, data_t *psData);
LPS altitude_init(LPS::sa0State addr);
void gyroreader(L3G gyro, data_t *gyroData);
L3G gyro_init(L3G::sa0State addr);
void accemagno(LSM303 accmag, data_t *accmaData);
LSM303 accemagno_init(LSM303::sa0State addr);

#endif /* IMUFUNCTIONS_H_ */