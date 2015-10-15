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
#define NUMBER_LED 4

const byte ledPins[NUMBER_LED] = {4, 5, 7, 6};

NewPing sonar(TRIGGER_UP, ECHO_UP, MAX_DISTANCE);

void setupObstacle()
{	
	pinMode(TRIGGER_UP, OUTPUT);
	pinMode(ECHO_UP, INPUT);
	
	for (byte i = 0; i < NUMBER_LED; i++) {
		pinMode(ledPins[i], OUTPUT);
	}
	
	pinMode(IR_RIGHT, INPUT);
	pinMode(IR_LEFT, INPUT);
}

void ultrasound(data_t* dataRead)
{
	//TODO: Add another ultrasound sensor on the foot
	unsigned long distance = 0;
	unsigned int usecs = 0;
	usecs = sonar.ping_median(ITERATIONS);
	distance = sonar.convert_cm(usecs);
	
	//Test
	driveActuators(0, distance);
	//Test end
	
	dataRead->data[0] = distance;
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
		//Serial.println("distance");
		ultrasound(&dataRead);
/*		infrared(&dataRead);*/
		stub_ob(i, &dataRead);
		i = (i+1)%2;
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
//	dprintf("%d: %d", id, (int)dist);
	if (on) {
		digitalWrite(ledPins[id], HIGH);
	} else {
		digitalWrite(ledPins[id], LOW);	
	}
}