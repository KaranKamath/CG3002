/*
 * debugging.h
 *
 * Created: 27/9/2015 4:21:03 PM
 *  Author: Linh
 */ 


#ifndef DEBUGGING_H_
#define DEBUGGING_H_
#include <Arduino.h>
#include <stdio.h>
#include "Wire.h"
void debugPrint(const char *str);
void dprintf(const char *fmt, ...);
int freeRam();


#endif /* DEBUGGING_H_ */