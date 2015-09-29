/*
 * debugging.cpp
 *
 * Created: 27/9/2015 4:20:49 PM
 *  Author: Linh
 */ 
#include "debugging.h"

char debugBuffer[100];

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

int freeRam() {
	extern int __heap_start, *__brkval;
	int v;
	return (int) &v - (__brkval == 0? (int)&__heap_start : (int) __brkval);
}