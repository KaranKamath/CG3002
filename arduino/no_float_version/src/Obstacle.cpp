/*
 * Obstacle.cpp
 *
 * Created: 29/9/2015 9:22:14 PM
 *  Author: Linh
 */ 

#include "global.h"
#include "Obstacle.h"
#include "UartComm.h"

//TODO: add more LED pin
#define NUMBER_LED 5

const byte ledPins[NUMBER_LED] = {47, 42, 41, 47, 45};
const byte OBSTACLE_THRESHOLD[NUMBER_LED] = {80, 80, 80, 80, 120};	
	
boolean front_on;

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

void ultrasound(NewPing sonar_right, NewPing sonar_left, NewPing sonar_stick, data_t* dataRead)
{
	unsigned long distance_right = 0;
	unsigned long distance_left = 0;
	unsigned long distance_stick = 0;
	
	unsigned int usecs_right = 0;
	unsigned int usecs_left = 0;
	unsigned int usecs_stick = 0;
	
	usecs_right = sonar_right.ping_median(ITERATIONS);
	distance_right = sonar_right.convert_cm(usecs_right);

	usecs_left = sonar_left.ping_median(ITERATIONS);
	distance_left = sonar_left.convert_cm(usecs_left);
	
	usecs_stick = sonar_stick.ping_median(ITERATIONS);
	distance_stick = sonar_stick.convert_cm(usecs_stick);
	
	driveActuators(1, distance_right);
	dataRead->data[1] = distance_right;
	driveActuators(2, distance_left);
	dataRead->data[2] = distance_left;
	driveActuators(3, distance_stick);
	dataRead->data[3] = distance_stick;
}

void infrared(data_t* dataRead)
{
	//TODO: add if clause to send negative value if nothing is in range?
	float sensorValue, infraDist;
	sensorValue = analogRead(IR_STICK);
	infraDist = 10650.08 * pow(sensorValue,-0.935) - 10;
	driveActuators(0, infraDist);
	dataRead->data[0] = infraDist;
	
	sensorValue = analogRead(IR_FRONT);
	infraDist = 10650.08 * pow(sensorValue,-0.935) - 10;
	driveActuators(4, infraDist);
	dataRead->data[4] = infraDist;
}

void readDistanceSensors(void *p)
{
	data_t dataRead;
	dataRead.id = IDOBSTACLE;
	
	NewPing sonar_right(TRIGGER_RIGHT, ECHO_RIGHT, MAX_DISTANCE);
	NewPing sonar_left(TRIGGER_LEFT, ECHO_LEFT, MAX_DISTANCE);
	NewPing sonar_stick(TRIGGER_STICK, ECHO_STICK, MAX_DISTANCE);
	
	while (1) {
		ultrasound(sonar_right, sonar_left, sonar_stick, &dataRead);
		infrared(&dataRead);
		//xQueueSendToBack(report, &dataRead, portMAX_DELAY);
		xQueueSendToBack(report, &dataRead, 500);
			
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
		front_on = on;
	}
	if (id == 0) {
		on |= front_on;
	}
	if (on) {
		digitalWrite(ledPins[id], HIGH);
	} else {
		digitalWrite(ledPins[id], LOW);	
	}
}