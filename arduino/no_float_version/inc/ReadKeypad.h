/*
 * Keypad.h
 *
 *  Author: Linh
 */ 

#ifndef READKEYPAD_H_
#define READKEYPAD_H_

#include "Keypad.h"
void setupKeypad(void);
void keyIsr(void);
void readKeypad(void *p);


#endif /* READKEYPAD_H_ */