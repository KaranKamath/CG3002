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

#define NUM_SONAR 3
#define TRIGGER_UP_LEFT 12
#define ECHO_UP_LEFT 11
#define TRIGGER_UP 4
#define ECHO_UP 3
#define TRIGGER_UP_RIGHT 8
#define ECHO_UP_RIGHT 9
#define TRIGGER_HAND 7
#define ECHO_HAND 6 
#define MAX_DISTANCE 300

#define ITERATIONS 3
#define OBSTACLE_THRESHOLD 80
#define OBSTACLE_HAND 70
#define MAX_PWM_VOLTAGE 127
#define IR_LEFT 15
#define IR_RIGHT 14
#define DELAY_DISTANCE 200

void setupObstacle(void);
void ultrasound(data_t* dataRead);
void infrared(data_t* dataRead);
void readDistanceSensors(void *p);

//Test
void driveActuators(byte id, float dist);


#endif /* OBSTACLE_H_ */