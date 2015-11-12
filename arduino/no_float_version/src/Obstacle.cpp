/*
 * Obstacle.cpp
 *
 * Created: 29/9/2015 9:22:14 PM
 *  Author: Linh
 */ 

#include "global.h"
#include "Obstacle.h"

//TODO: add more LED pin
#define NUMBER_LED 5

const byte ledPins[NUMBER_LED] = {47, 42, 41, 47, 45};
const byte OBSTACLE_THRESHOLD[NUMBER_LED] = {80, 50, 50, 80, 120};	
	
boolean stick_on;
boolean down;

void setupObstacle()
{	
	pinMode(TRIGGER_RIGHT, OUTPUT);
	pinMode(ECHO_RIGHT, INPUT);
	
	pinMode(TRIGGER_LEFT,OUTPUT);
	pinMode(ECHO_LEFT, INPUT);
	
	pinMode(TRIGGER_STICK, OUTPUT);
	pinMode(ECHO_STICK, INPUT);
	
	for (byte i = 0; i < NUMBER_LED; i++) {
		pinMode(ledPins[i], OUTPUT);
	}
}

void readDistanceSensors(void *p)
{
	unsigned long distance_right = 0;
	unsigned long distance_left = 0;
	unsigned long distance_stick = 0;
	
	unsigned int usecs_right = 0;
	unsigned int usecs_left = 0;
	unsigned int usecs_stick = 0;
	
	float sensorValue, infraDist;
	
	NewPing sonar_right(TRIGGER_RIGHT, ECHO_RIGHT, MAX_DISTANCE);
	NewPing sonar_left(TRIGGER_LEFT, ECHO_LEFT, MAX_DISTANCE);
	NewPing sonar_stick(TRIGGER_STICK, ECHO_STICK, MAX_DISTANCE + 30);
	
	while (1) {
		usecs_right = sonar_right.ping_median(ITERATIONS);
		distance_right = sonar_right.convert_cm(usecs_right);
		driveActuators(1, distance_right);
		
		usecs_left = sonar_left.ping_median(ITERATIONS);
		distance_left = sonar_left.convert_cm(usecs_left);
		driveActuators(2, distance_left);
		
		usecs_stick = sonar_stick.ping_median(ITERATIONS);
		distance_stick = sonar_stick.convert_cm(usecs_stick);
		driveActuators(3, distance_stick);
		
		sensorValue = analogRead(IR_STICK);
		infraDist = 10650.08 * pow(sensorValue,-0.935) - 10;
		driveActuators(0, infraDist);
		
		sensorValue = analogRead(IR_FRONT);
		infraDist = 10650.08 * pow(sensorValue,-0.935) - 10;
		driveActuators(4, infraDist);

		vTaskDelay(DELAY_DISTANCE);
	}		
}

void driveActuators(byte id, float dist)
{
	if (id >= NUMBER_LED) {
		return;
	}
	bool on = (dist > 0 && dist < OBSTACLE_THRESHOLD[id]);
	if (id == 3) {
		stick_on = on;
		down = (dist > 110);
	}
	if (id == 0) {
		on |= stick_on;
	}
	on |= down;
	if (on) {
		digitalWrite(ledPins[id], HIGH);
	} else {
		digitalWrite(ledPins[id], LOW);	
	}
}