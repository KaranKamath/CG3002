/*
* ObstacleDetection.cpp
*
* Created: 9/29/2015 10:02:37 AM
*  Author: Asawari
*/

#include <avr/io.h>
#include <FreeRTOS.h>
#include <task.h>
#include <queue.h>
#include <semphr.h>
#include <Arduino.h>

#include "NewPing.h"

#define TRIGGER_PIN 12
#define ECHO_PIN 11
#define MAX_DISTANCE 200
#define ITERATIONS 5
#define OBSTACLE_THRESHOLD 80
#define MAX_PWM_VOLTAGE 127

#define sensorIR 15

/* Global Variables */
int motor1Pins[2] = {4, 5};
bool runMotor1 = false;
int motor2Pins[2] = {7, 6};
bool runMotor2 = false;


NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);

char debugBuffer[1024];
void debugPrint(const char *str)
{
	Serial.println(str);
	Serial.flush();
}
void dprintf(const char *fmt, ...)
{
	va_list argptr;
	va_start(argptr, fmt);
	vsprintf(debugBuffer, fmt, argptr);
	va_end(argptr);
	debugPrint(debugBuffer);
}

void setup()
{
	/* Initialize the UART port */
	Serial.begin(9600);
	
	/* Initialize the Ultrasound Sensor */

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
	//unsigned long pulseTime = 0;  // Variable for reading the pulse
	unsigned long distance = 0;
	unsigned int usecs = 0;
	float sensorValue, infraDist;
	
	while(1)
	{
		usecs = sonar.ping_median(ITERATIONS);
		distance = sonar.convert_cm(usecs);
		//dprintf("Raw Distance:%d cm",distance);
		runMotor1 = false;
		runMotor2 = false;
		
		if(((0<distance) && (distance<OBSTACLE_THRESHOLD))){
			dprintf("OBSTACLE DETECTED ! At Distance:%d cm",distance);
			//Start Actuator Task
			runMotor1 = true;
		}

		sensorValue = analogRead(sensorIR);
		infraDist = 10650.08 * pow(sensorValue,-0.935) - 10;
		//infraDist = 4192.936 * pow(sensorValue,-0.935) - 3.937;
		
		if(((20<infraDist) && (infraDist<OBSTACLE_THRESHOLD))){
			dprintf("INFRARED OBSTACLE DETECTED ! At Distance:%d inches",(int)infraDist);
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

#define STACK_DEPTH 512

void vApplicationIdleHook()
{
	//Do nothing.
}

int main(void)
{
	init();
	setup();
	
	//Create tasks

	xTaskCreate(readDistanceSensors,"Ultrasound and Infrared",STACK_DEPTH,NULL,1,NULL);
	xTaskCreate(driveActuators,"Drive Motors",STACK_DEPTH,NULL,1,NULL);

	vTaskStartScheduler();
}
