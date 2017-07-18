/**
 *
 * pins.h
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * RPi pins used for CK2 Pro hat connectivity
 *
 */


#ifndef __CK2_PRO_PINS_H__
#define __CK2_PRO_PINS_H__


#include <wiringPi.h>

#include "detection.h"


/**
 * Detection
 *
 * Raised pins:
 *     Phys 18, BCM 24, Detection Pin 3
 *
 * All other pins actively lowered
 */
static union detection_pin_state CK2_PRO_DETECTION_SIGNATURE = {
    .pin = {
        .__unused = 0,
        .pin_1 = 0,
        .pin_2 = 0,
        .pin_3 = 1,
        .pin_4 = 0,
        .pin_5 = 0,
    }
};


#endif  // __CK2_PRO_PINS_H__
