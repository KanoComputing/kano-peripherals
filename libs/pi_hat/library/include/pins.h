/**
 *
 * pins.h
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * RPi pins used for hat connectivity
 *
 */


#ifndef __PINS_H__
#define __PINS_H__


#include <wiringPi.h>


static const int POWER_PIN = 3;  // Phys 5, BCM 3
static const int DEFAULT_POWER_PIN_STATE = PUD_DOWN;

static const int LOW_BATTERY_PIN = 16;  // Phys 36, BCM 16
static const int LOW_BATTERY_TRIGGER_VALUE = 1;



#endif  // __CK2_PRO_PINS_H__
