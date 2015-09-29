/*
 * Obstacle.cpp
 *
 * Created: 29/9/2015 9:22:14 PM
 *  Author: Linh
 */ 

#include "Obstacle.h"
#include "debugging.h"

//TODO: change to array of actuators
const byte motor1Pins[2] = {4, 5};
bool runMotor1 = false;
const byte motor2Pins[2] = {7, 6};
bool runMotor2 = false;

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);

void setupObstacle()
{	
	// Make the init pin an output:
	pinMode(TRIGGER_PIN, OUTPUT);
	// Make the echo pin an input:
	pinMode(ECHO_PIN, INPUT);
	
	//Initialize Motor pins
	pinMode(motor1Pins[0],OUTPUT);
	pinMode(motor1Pins[1],OUTPUT);
	
	//Initialize Motor pins
	pinMode(motor2Pins[0],OUTPUT);
	pinMode(motor2Pins[1],OUTPUT);

}

void readDistanceSensors(void *p)
{
	unsigned long distance = 0;
	unsigned int usecs = 0;
	float sensorValue, infraDist;
	
	while(1)
	{
		usecs = sonar.ping_median(ITERATIONS);
		distance = sonar.convert_cm(usecs);
		runMotor1 = false;
		runMotor2 = false;
		
		if ((0 < distance) && (distance < OBSTACLE_THRESHOLD)) {
			dprintf("ULTRA: %d cm",distance);
			//Start Actuator Task
			runMotor1 = true;
		}

		sensorValue = analogRead(sensorIR);
		infraDist = 10650.08 * pow(sensorValue,-0.935) - 10;
		//infraDist = 4192.936 * pow(sensorValue,-0.935) - 3.937;
		
		if ((20 < infraDist) && (infraDist < OBSTACLE_THRESHOLD)) {
			dprintf("INFRARED: %d",(int)infraDist);
			//Start Actuator Task
			runMotor2 = true;
		}

		vTaskDelay(100);
	}
}


void driveActuators(void* pvParameters)
{
	
	/* Infinite loop */
	while (1)
	{
		/* Vibrate Motor 1 */

		if (runMotor1) {
			/* Turn Motor On */
			analogWrite(motor1Pins[1], MAX_PWM_VOLTAGE);
			digitalWrite(motor1Pins[0], LOW);
		} else {
			/* Turn Motor Off */
			digitalWrite(motor1Pins[1], LOW);
			digitalWrite(motor1Pins[0], LOW);
		}
		
		if (runMotor2) {
			/* Turn Motor On */
			digitalWrite(motor2Pins[1], MAX_PWM_VOLTAGE);
			digitalWrite(motor2Pins[0], LOW);
		} else {
			/* Turn Motor Off */
			digitalWrite(motor2Pins[1], LOW);
			digitalWrite(motor2Pins[0], LOW);	
		}
	}
}