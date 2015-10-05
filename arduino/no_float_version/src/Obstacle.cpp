/*
 * Obstacle.cpp
 *
 * Created: 29/9/2015 9:22:14 PM
 *  Author: Linh
 */ 

#include "Obstacle.h"
#include "debugging.h"

#define NUMBER_MOTOR 2

const byte motorPins[2*NUMBER_MOTOR] = {4, 5, 7, 6};
bool runMotor[NUMBER_MOTOR] = {false, false};

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);

void setupObstacle()
{	
	// Make the init pin an output:
	pinMode(TRIGGER_PIN, OUTPUT);
	// Make the echo pin an input:
	pinMode(ECHO_PIN, INPUT);

	byte i = 0;
	for (i = 0; i < 2*NUMBER_MOTOR; i++) {
		pinMode(motorPins[i], OUTPUT);
	}
}

void readDistanceSensors(void *p)
{
	unsigned long distance = 0;
	unsigned int usecs = 0;
	float sensorValue, infraDist;
	
	while(1)
	{
		byte i;
		usecs = sonar.ping_median(ITERATIONS);
		distance = sonar.convert_cm(usecs);

		for (i = 0; i < NUMBER_MOTOR; i++) {
			runMotor[i] = false;
		}
		if ((0 < distance) && (distance < OBSTACLE_THRESHOLD)) {
			dprintf("ULTRA: %d cm",distance);
			//Start Actuator Task
			runMotor[0] = true;
		}

		sensorValue = analogRead(sensorIR);
		infraDist = 10650.08 * pow(sensorValue,-0.935) - 10;
		
		if ((20 < infraDist) && (infraDist < OBSTACLE_THRESHOLD)) {
			dprintf("INFRARED: %d",(int)infraDist);
			//Start Actuator Task
			runMotor[1] = true;
		}

		vTaskDelay(100);
	}
}


void driveActuators(void* pvParameters)
{
	
	/* Infinite loop */
	while (1)
	{
		byte i;
		/* Vibrate Motor 1 */
		for (i = 0; i < NUMBER_MOTOR; i++) {
			if (runMotor[i]) {
			/* Turn Motor On */
				analogWrite(motorPins[2*i+1], MAX_PWM_VOLTAGE);
				digitalWrite(motorPins[2*i], LOW);
			} else {
			/* Turn Motor Off */
				digitalWrite(motorPins[2*i+1], LOW);
				digitalWrite(motorPins[2*i], LOW);
			}
		}
	}
}