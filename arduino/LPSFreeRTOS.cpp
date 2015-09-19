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

LPS ps;

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
  Serial.begin(9600);
  Wire.begin();

  if (!ps.init())
  {
	  dprintf("Failed to autodetect pressure sensor!");
	  while (1);
  }

  ps.enableDefault();
}

void task1(void *p)
{
	while(1)
	{
		//float pressure = ps.readPressureMillibars();
		//float altitude = ps.pressureToAltitudeMeters(pressure);

		dprintf("Altitude:");

		vTaskDelay(5000);
	}
}



#define STACK_DEPTH 2048

void vApplicationIdleHook()
{
	//Do nothing.
}


int main(void)
{
	init();
	setup();
	TaskHandle_t t1;
		
	//Create tasks
	xTaskCreate(task1,"Task 1",STACK_DEPTH,NULL,1,&t1);

	vTaskStartScheduler();	
}

