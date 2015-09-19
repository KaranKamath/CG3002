/*
* FreeRTOS2560.cpp
*
* Created: 9/1/2015 10:43:58 PM
*  Author: Asawari
*/


#include <avr/io.h>
#include <FreeRTOS.h>
#include <task.h>
#include <Arduino.h>

#include <Wire.h>
#include <LPS.h>

#define TRIGGER_PIN 12
#define ECHO_PIN 11
unsigned long pulseTime = 0;  // variable for reading the pulse
unsigned long distance = 0;


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
  // make the init pin an output:
  pinMode(TRIGGER_PIN, OUTPUT);
  // make the echo pin an input:
  pinMode(ECHO_PIN, INPUT);
  // initialize the serial port:
  Serial.begin(9600);
}

void task1(void *p)
{
	while(1)
	{
		// send the sensor a 10microsecond pulse:
		digitalWrite(TRIGGER_PIN, HIGH);
		delayMicroseconds(10);
		digitalWrite(TRIGGER_PIN, LOW);
		
		// wait for the pulse to return. The pulse
		// goes from low to HIGH to low, so we specify
		// that we want a HIGH-going pulse below:

		pulseTime = pulseIn(ECHO_PIN, HIGH);
		distance = pulseTime/58;
		// print out that number
		//Serial.println(pulseTime, DEC);
		//Serial.println(distance,DEC);

		dprintf("Distance:%d cm",distance);

		vTaskDelay(2000);
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
	//TaskHandle_t t1;
		
	//Create tasks
	xTaskCreate(task1,"Task 1",STACK_DEPTH,NULL,1,NULL);

	vTaskStartScheduler();	
}

