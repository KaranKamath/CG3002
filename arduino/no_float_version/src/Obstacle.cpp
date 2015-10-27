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
#define NUMBER_LED 6
#define NUM_MOTORS 1
//#define FILTER_WINDOW 5

const byte ledPins[NUMBER_LED] = {42, 43, 44, 45, 46, 47};


NewPing sonar_up(TRIGGER_UP, ECHO_UP, MAX_DISTANCE);
NewPing sonar_up_left(TRIGGER_UP_LEFT, ECHO_UP_LEFT, MAX_DISTANCE);
NewPing sonar_up_right(TRIGGER_UP_RIGHT, ECHO_UP_RIGHT, MAX_DISTANCE);
NewPing sonar_hand(TRIGGER_HAND,ECHO_HAND,MAX_DISTANCE);

void setupObstacle()
{	
	pinMode(TRIGGER_UP, OUTPUT);
	pinMode(ECHO_UP, INPUT);
	
	pinMode(TRIGGER_UP_LEFT,OUTPUT);
	pinMode(ECHO_UP_LEFT, INPUT);
	
	pinMode(TRIGGER_UP_RIGHT,OUTPUT);
	pinMode(ECHO_UP_RIGHT, INPUT);
	
	pinMode(TRIGGER_HAND,OUTPUT);
	pinMode(ECHO_HAND, INPUT);	
	
	for (byte i = 0; i < NUMBER_LED; i++) {
		pinMode(ledPins[i], OUTPUT);
	}	
}

void ultrasound(data_t* dataRead)
{
	//TODO: Add another ultrasound sensor on the foot
	unsigned long distance = 0;
	unsigned long distance_up_left = 0;
	unsigned long distance_up_right = 0;
	unsigned long distance_hand = 0;
	//unsigned long dist_buff[FILTER_WINDOW];
	//unsigned long dist_left_buff[FILTER_WINDOW];
	//unsigned long dist_right_buff[FILTER_WINDOW];
	//int dist_ind = 0, dist_left_ind = 0, dist_right_ind = 0 ;
	unsigned int usecs = 0;
	unsigned int usecs_up_left = 0;
	unsigned int usecs_up_right = 0;
	unsigned int usecs_hand = 0;
	
	
	usecs = sonar_up.ping_median(ITERATIONS);
	distance = sonar_up.convert_cm(usecs);
	//dist_buff[(dist_ind%5)] = distance;
	//dist_ind++;
	//sort(&dist_buff);
	//filtered_dist = dist_buff[]
	
	usecs_up_left = sonar_up_left.ping_median(ITERATIONS);
	distance_up_left = sonar_up_left.convert_cm(usecs_up_left);
	//dist_left_buff[(dist_left_ind%5)] = distance;
	//dist_left_ind++;
	//sort(&dist_left_buff);
	
	usecs_up_right = sonar_up_right.ping_median(ITERATIONS);
	distance_up_right = sonar_up_right.convert_cm(usecs_up_right);
	//dist_right_buff[(dist_right_ind%5)] = distance;
	//dist_right_ind++;
	//sort(&dist_right_buff);
	
	usecs_hand = sonar_hand.ping_median(ITERATIONS);
	distance_hand = sonar_hand.convert_cm(usecs_hand);
	
	driveActuators(0, distance);
	dataRead->data[0] = distance;
	driveActuators(3, distance_up_left);
	dataRead->data[3] = distance_up_left;
	driveActuators(4, distance_up_right);	
	dataRead->data[4] = distance_up_right;
	
	driveActuators(5, distance_hand);
	
}

void infrared(data_t* dataRead)
{
	//TODO: add if clause to send negative value if nothing is in range?
	float sensorValue, infraDist;
	sensorValue = analogRead(IR_LEFT);
	infraDist = 10650.08 * pow(sensorValue,-0.935) - 10;
	
	//Test
	driveActuators(1, infraDist);
	//Test end
	
	dataRead->data[1] = infraDist;
	sensorValue = analogRead(IR_RIGHT);
	infraDist = 10650.08 * pow(sensorValue,-0.935) - 10;
	
	driveActuators(2, infraDist);
	
	dataRead->data[2] = infraDist;
}

void stub_ob(int i, data_t* dataRead) {
	int j = 1;
	for (j = 1; j < 5; j++) {
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
//		stub_ob(i, &dataRead);
//		i = (i+1)%2;
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
	bool on;
	if (id < 5) {
		on = (dist > 0 && dist < OBSTACLE_THRESHOLD);
	}else {
		on = (dist > 0 && dist < OBSTACLE_HAND);
	}	
	if (on) {
		digitalWrite(ledPins[id], HIGH);
	} else {
		digitalWrite(ledPins[id], LOW);	
	}
}