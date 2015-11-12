/*
 * global.h
 *
 * Created: 27/9/2015 4:49:27 PM
 *  Author: Linh
 */ 


#ifndef GLOBAL_H_
#define GLOBAL_H_

#include <avr/io.h>
#include <FreeRTOS.h>
#include <semphr.h>
#include <Arduino.h>
#include <task.h>
#include <stdio.h>
#include "Wire.h"
#include "queue.h"

#define MAX_NUM_DATA 10
#define DELAY_IMU 200

#define IDDOWN 0
#define IDUP 1
#define IDOBSTACLE 2
#define OFFSETAM 1
#define OFFSETGY 7

typedef struct {
	byte id;
	int data[MAX_NUM_DATA];
	} data_t;
#endif /* GLOBAL_H_ */