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

#define QUEUE_SIZE 5
#define MAX_NUM_DATA 10
#define DELAY_IMU 200
#define STACK_DEPTH 190

#define IDIMU 0
#define IDOBSTACLE 1
#define OFFSETAM 1
#define OFFSETGY 7

#define LED_PIN 38

typedef struct {
	byte id;
	int data[MAX_NUM_DATA];
	} data_t;
#endif /* GLOBAL_H_ */