/*
 * UartComm.h
 *
 * Created: 27/9/2015 11:02:39 PM
 *  Author: Linh
 */ 


#ifndef UARTCOMM_H_
#define UARTCOMM_H_

#include "global.h"
#include "debugging.h"
extern xQueueHandle report;
void setupUart();
void sendData(void *p);

#endif /* UARTCOMM_H_ */