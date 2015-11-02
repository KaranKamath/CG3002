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

#define NUM_SONAR 2

#define TRIGGER_LEFT 12
#define ECHO_LEFT 11
#define TRIGGER_RIGHT 8
#define ECHO_RIGHT 9
#define TRIGGER_STICK 7
#define ECHO_STICK 6

#define MAX_DISTANCE 300

#define ITERATIONS 3
#define MAX_PWM_VOLTAGE 127
#define IR_STICK 15
#define IR_FRONT 14
#define DELAY_DISTANCE 200

void setupObstacle(void);
void ultrasound(data_t* dataRead);
void infrared(data_t* dataRead);
void readDistanceSensors(void *p);

//Test
void driveActuators(byte id, float dist);


#endif /* OBSTACLE_H_ */