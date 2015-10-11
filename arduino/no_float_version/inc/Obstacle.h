/*
 * Obstacle.h
 *
 * Created: 29/9/2015 9:18:44 PM
 *  Author: Linh
 */ 


#ifndef OBSTACLE_H_
#define OBSTACLE_H_

#include "global.h"
#include "NewPing.h"

#define TRIGGER_PIN 12
#define ECHO_PIN 11
#define MAX_DISTANCE 200
#define ITERATIONS 5
//#define OBSTACLE_THRESHOLD 80
//#define MAX_PWM_VOLTAGE 127
#define IR_PIN_LEFT 15
#define IR_PIN_RIGHT 14

extern xQueueHandle report;

void setupObstacle(void);
void readDistanceSensors(void *p);
//void driveActuators(void* pvParameters);
void ultrasound(data_t *psData);
void infrared_left(data_t *psData);
void infrared_right(data_t *psData);

#endif /* OBSTACLE_H_ */