/*
 * Keypad.h
 *
 *  Author: Linh
 */ 

#ifndef KEYPAD_H_
#define KEYPAD_H_

void setupKeypad(void);
void key_isr(void);
void read_keypad(void *p);


#endif /* KEYPAD_H_ */