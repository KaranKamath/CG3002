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
#include <Keypad.h>
#include <LSM303.h>
#include <L3G.h>
//#include <NewPing.h>


//Tasks flash LEDs at Pins 12 and 13 at 1Hz and 2Hz respectively.
void task1(void *p)
{
	while(1)
	{
		digitalWrite(32,HIGH);
		vTaskDelay(500);//Delay for 500 ticks. Since each tick is 1ms,
		//this delays for 500ms.
		digitalWrite(32,LOW);
		vTaskDelay(500);
	}
}

void task2(void *p)
{
	while(1)
	{
		digitalWrite(13,HIGH);
		vTaskDelay(250);
		digitalWrite(13,LOW);
		vTaskDelay(250);
	}
}
#define STACK_DEPTH 64

void vApplicationIdleHook()
{
	//Do nothing.
}

int main(void)
{
	init();
	pinMode(32,OUTPUT);
	pinMode(13,OUTPUT);
	TaskHandle_t t1,t2;
	
	//Create tasks
	xTaskCreate(task1,"Task 1",STACK_DEPTH,NULL,6,&t1);
	xTaskCreate(task2,"Task 2",STACK_DEPTH,NULL,5,&t2);
	vTaskStartScheduler();
	
}

