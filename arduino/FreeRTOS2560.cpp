/*
* FreeRTOS2560.cpp
*
* Created: 9/1/2015 10:43:58 PM
*  Author: Asawari
*/


#include <avr/io.h>
#include <FreeRTOS.h>
#include <task.h>
#include <queue.h>
#include <Arduino.h>

//#include "Wire.h"
//#include "LPS.h"

//LPS ps;
#define TRIGGER_PIN 12
#define ECHO_PIN 11
unsigned long pulseTime = 0;  // variable for reading the pulse
unsigned long distance = 0;

char ack[50];
int cntFlag;
char ackData[50];

/* Global Variables */
xQueueHandle xQueue;

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
	/* Initialize the uart port */
	Serial.begin(9600);
	Serial1.begin(9600);
	
	while (cntFlag == 0){
		if (strcmp(ack,"ACK")!= 0) {
			char handshake[10];
			strcpy(handshake, "BEGIN\n");
			Serial1.write(handshake);
			delay(200);
			int numRecieved = Serial1.available();
			if(numRecieved > 0){
				Serial1.readBytesUntil(0,ack,3);
			}
			Serial.write(ack);
			} else {
			//echo ACK
			if (cntFlag == 0) {
				Serial.write(ack);
				char ackSend[5];
				strcpy(ackSend, "ACK\n");
				Serial1.write(ackSend);
				cntFlag++;
			}
			Serial.println("Count Flag is");
			Serial.println(cntFlag);
		}
	}
	
	//Serial.begin(9600);
	//Wire.begin();

	//if (!ps.init())
	//{
	//dprintf("Failed to autodetect pressure sensor!");
	// while (1);
	//}

	//ps.enableDefault();
	// make the init pin an output:
	pinMode(TRIGGER_PIN, OUTPUT);
	// make the echo pin an input:
	pinMode(ECHO_PIN, INPUT);
}

/*int freeRam () {
extern int __heap_start, *__brkval;
int v;
return ((int) &v –(__brkval == 0 ? (int) &__heap_start : (int) __brkval));
}*/

/*void task1(void *p)
{
while(1)
{
float pressure = ps.readPressureMillibars();
float altitude = ps.pressureToAltitudeMeters(pressure);

int alt = (int)(altitude*1000);

dprintf("Altitude: %d mm",alt);

vTaskDelay(500);
}
}
*/

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
		
		/* Put the read value on the queue */
		xQueueSendToBack(xQueue, &distance, 0);

		//dprintf("Distance:%d cm",distance);

		vTaskDelay(500);
	}
}

void task2(void* pvParameters)
{
	int dist_meas;
	int samplecount = 0;
	char report[80];

	/* Infinite loop */
	while (1)
	{
		/* Wait until an element is received from the queue */
		if (xQueueReceive(xQueue, &dist_meas, portMAX_DELAY))
		{
			do {
				samplecount++;
				/* Print the result on the uart port */
				//dprintf("%d Distance:%d cm", samplecount, dist_meas);
				snprintf(report, sizeof(report), "%d Distance:%d cm\n", samplecount, dist_meas);
				Serial1.write(report);
				Serial.println(report);							
				memset(ackData, 0, sizeof(ackData));
				int numRecieved = Serial1.available();
				if (numRecieved > 0){
					Serial1.readBytesUntil(0, ackData, 3);
					Serial.println(ackData);
				}
			} while(strcmp(ackData,"ACK")!=0);
			
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
	//TaskHandle_t t1;
	
	//dprintf("RAM: %d ",freeRam());
	
	/* Create the Queue for communication between the tasks */
	xQueue = xQueueCreate( 5, sizeof(int) );
	
	//Create tasks
	xTaskCreate(task1,"Task 1",STACK_DEPTH,NULL,1,NULL);
	xTaskCreate(task2,"Task 2",STACK_DEPTH,NULL,1,NULL);

	vTaskStartScheduler();
}

