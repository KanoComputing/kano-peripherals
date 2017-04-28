/**
 *
 * pins.h
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * RPi pins used for CK2 Lite hat connectivity
 *
 */


#ifndef __CK2_LITE_PINS_H__
#define __CK2_LITE_PINS_H__


#include <wiringPi.h>

#include "detection.h"


/**
 * Detection
 *
 * Raised pins:
 *     Phys 37, BCM 26, Detection Pin 4
 */
static union detection_pin_state CK2_LITE_DETECTION_SIGNATURE = {
    // .value = 0b00010
    .pin = {
        .pin_1 = 0,
        .pin_2 = 0,
        .pin_3 = 0,
        .pin_4 = 1,
        .pin_5 = 0,
    }
};


static const int LED_PIN = 18;  // Phys 12, BCM 18


#endif  // __CK2_LITE_PINS_H__
