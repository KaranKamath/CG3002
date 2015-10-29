/*
 * Obstacle.cpp
 *
 * Created: 29/9/2015 9:22:14 PM
 *  Author: Linh
 */ 

#include "global.h"
#include "Obstacle.h"
#include "UartComm.h"
#include "debugging.h"

//TODO: add more LED pin
#define NUMBER_LED 5

const byte ledPins[NUMBER_LED] = {40, 41, 42, 43, 44};

NewPing sonar_up(TRIGGER_RIGHT, ECHO_RIGHT, MAX_DISTANCE);
NewPing sonar_down(TRIGGER_LEFT, ECHO_LEFT, MAX_DISTANCE);
NewPing sonar_hand(TRIGGER_HAND, ECHO_HAND, MAX_DISTANCE);
//NewPing sonar_front(TRIGGER_FRONT, ECHO_FRONT, MAX_DISTANCE);

void setupObstacle()
{	
	pinMode(TRIGGER_RIGHT, OUTPUT);
	pinMode(ECHO_RIGHT, INPUT);
	
	pinMode(TRIGGER_LEFT,OUTPUT);
	pinMode(ECHO_LEFT, INPUT);
	
	pinMode(TRIGGER_HAND, OUTPUT);
	pinMode(ECHO_HAND, INPUT);
	
//	pinMode(TRIGGER_FRONT, OUTPUT);
//	pinMode(ECHO_FRONT, INPUT);
	
	for (byte i = 0; i < NUMBER_LED; i++) {
		pinMode(ledPins[i], OUTPUT);
	}
}

void ultrasound(data_t* dataRead)
{
	//TODO: Add another ultrasound sensor on the foot
	unsigned long distance = 0;
	unsigned long distance_down = 0;
	unsigned long distance_hand = 0;
	
	unsigned int usecs = 0;
	unsigned int usecs_down = 0;
	unsigned int usecs_hand = 0;
	
	usecs = sonar_up.ping_median(ITERATIONS);
	distance = sonar_up.convert_cm(usecs);

	usecs_down = sonar_down.ping_median(ITERATIONS);
	distance_down = sonar_down.convert_cm(usecs_down);
	
	usecs_hand = sonar_hand.ping_median(ITERATIONS);
	distance_hand = sonar_hand.convert_cm(usecs_hand);
	
	driveActuators(1, distance);
	dataRead->data[1] = distance;
	driveActuators(2, distance_down);
	dataRead->data[2] = distance_down;
	driveActuators(3, distance_hand);
	dataRead->data[3] = distance_hand;
}

void infrared(data_t* dataRead)
{
	//TODO: add if clause to send negative value if nothing is in range?
	float sensorValue, infraDist;
	sensorValue = analogRead(IR_STICK);
	infraDist = 10650.08 * pow(sensorValue,-0.935) - 10;
	
	//Test
	driveActuators(0, infraDist);
	//Test end
	
	dataRead->data[0] = infraDist;
	
	sensorValue = analogRead(IR_FRONT);
	infraDist = 10650.08 * pow(sensorValue,-0.935) - 10;
	driveActuators(4, infraDist);
	dataRead->data[4] = infraDist;
	
}

void stub_ob(int i, data_t* dataRead) {
	int j = 1;
	for (j = 1; j < 4; j++) {
		dataRead->data[j] = 0;
	}
}
void readDistanceSensors(void *p)
{
	data_t dataRead;
	dataRead.id = IDOBSTACLE;
	byte i = 0;
	while (1) {
		ultrasound(&dataRead);
		infrared(&dataRead);
		//xQueueSendToBack(report, &dataRead, portMAX_DELAY);
		xQueueSendToBack(report, &dataRead, 500);
			
		vTaskDelay(DELAY_DISTANCE);
	}		
}

//Testing purpose
void driveActuators(byte id, float dist)
{
	if (id >= NUMBER_LED) {
		return;
	}
	bool on = (dist > 0 && dist < OBSTACLE_THRESHOLD);
	if (on) {
		digitalWrite(ledPins[id], HIGH);
	} else {
		digitalWrite(ledPins[id], LOW);	
	}
}