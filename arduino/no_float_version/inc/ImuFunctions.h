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

typedef struct {
	LPS ps;
	xQueueHandle queue;
	} para_ps_t;

extern L3G gyro;
extern xQueueHandle report;
	
void altitude(void *p);
void accemagno (void *p);
void accemagno_init(void) ;

#endif /* IMUFUNCTIONS_H_ */