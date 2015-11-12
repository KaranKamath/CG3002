/*
 * UartComm.h
 *
 * Created: 27/9/2015 11:02:39 PM
 *  Author: Linh
 */ 


#ifndef UARTCOMM_H_
#define UARTCOMM_H_

#include "global.h"

void setupUart();
void handshake(void);
void sendData(data_t received);

#endif /* UARTCOMM_H_ */