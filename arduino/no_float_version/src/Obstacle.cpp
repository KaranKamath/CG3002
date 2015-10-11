/*
 * Obstacle.cpp
 *
 * Created: 29/9/2015 9:22:14 PM
 *  Author: Linh
 */ 

#include "Obstacle.h"
#include "debugging.h"

//#define NUMBER_MOTOR 2

//const byte motorPins[2*NUMBER_MOTOR] = {4, 5, 7, 6};
//bool runMotor[NUMBER_MOTOR] = {false, false};

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);

void setupObstacle()
{	
	// Make the init pin an output:
	pinMode(TRIGGER_PIN, OUTPUT);
	// Make the echo pin an input:
	pinMode(ECHO_PIN, INPUT);
	
	/*for (byte i = 0; i < 2*NUMBER_MOTOR; i++) {
		pinMode(motorPins[i], OUTPUT);
	}*/
}

void readDistanceSensors(void *p) {
	data_t dataRead;
	while (1) {
		//Serial.println("distance");
		ultrasound(&dataRead);
		xQueueSendToBack(report, &dataRead, 500);
		
		infrared_left(&dataRead);
		xQueueSendToBack(report, &dataRead, 500);
		
		infrared_right(&dataRead);
		xQueueSendToBack(report, &dataRead, 500);
		
		vTaskDelay(DELAY_DISTANCE);
	}
}

void ultrasound(data_t *psData) {
	psData->id = IDULTRA;
	unsigned long distance = 0;
	unsigned int usecs = 0;
	usecs = sonar.ping_median(ITERATIONS);
	distance = sonar.convert_cm(usecs);
	psData->data[0] = distance;
}

void infrared_left(data_t *psData) {
	psData->id = IDINFRALEFT;
	float sensorValue, infraDist;
	sensorValue = analogRead(IR_PIN_LEFT);
	infraDist = 10650.08 * pow(sensorValue,-0.935) - 10;
	psData->data[0] = infraDist;
}

void infrared_right(data_t *psData) {
	psData->id = IDINFRARIGHT;
	float sensorValue, infraDist;
	sensorValue = analogRead(IR_PIN_RIGHT);
	infraDist = 10650.08 * pow(sensorValue,-0.935) - 10;
	psData->data[0] = infraDist;
}


/*void readDistanceSensors(void *p)
{
	unsigned long distance = 0;
	unsigned int usecs = 0;
	float sensorValue, infraDist;
	
	while(1)
	{
		usecs = sonar.ping_median(ITERATIONS);
		distance = sonar.convert_cm(usecs);

		for (byte i = 0; i < NUMBER_MOTOR; i++) {
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
			dprintf("INFRA: %d",(int)infraDist);
			//Start Actuator Task
			runMotor[1] = true;
		}

		vTaskDelay(100);
	}
}*/


//void driveActuators(void* pvParameters)
///{
	
	/* Infinite loop */
	//while (1)
	//{
		/* Vibrate Motor 1 */
		//for (byte i = 0; i < NUMBER_MOTOR; i++) {
			//if (runMotor[i]) {
			/* Turn Motor On */
			//	analogWrite(motorPins[2*i+1], MAX_PWM_VOLTAGE);
			//	digitalWrite(motorPins[2*i], LOW);
			//} else {
			/* Turn Motor Off */
			//	digitalWrite(motorPins[2*i+1], LOW);
			//	digitalWrite(motorPins[2*i], LOW);
			//}
		//}
	//}
//}