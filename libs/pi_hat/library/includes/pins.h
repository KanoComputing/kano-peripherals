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
static const int LED_PIN = 18;  // Phys 12, BCM 18
static const int DETECTION_PIN = 26;  // Phys 37, BCM 26

static const int DEFAULT_POWER_PIN_STATE = PUD_DOWN;
static const int DEFAULT_DETECTION_PIN_STATE = PUD_UP;

static const int DEFAULT_DETECTION_PIN_VAL = 1;


#endif  // __PINS_H__
