/**
 *
 * detection.c
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Hat detection and connectivity functions
 *
 */


#include <stdbool.h>
#include <wiringPi.h>

#include "callbacks.h"
#include "err.h"

#include "pins.h"
#include "detection.h"


/**
 * Sets up the detection system.
 *
 * Fails with E_HAT_NOT_ATTACHED if the hat isn't present
 */
int initialise_detection()
{
    pullUpDnControl(DETECTION_PINS.pin_1, PUD_DOWN);
    pullUpDnControl(DETECTION_PINS.pin_2, PUD_DOWN);
    pullUpDnControl(DETECTION_PINS.pin_3, PUD_DOWN);
    pullUpDnControl(DETECTION_PINS.pin_4, PUD_DOWN);
    // Quirky pin which opposes the expectation
    pullUpDnControl(DETECTION_PINS.pin_5, PUD_UP);

    return SUCCESS;
}


int clean_up_detection()
{
    return SUCCESS;
}


union detection_pin_state read_detection_pins(void)
{
    union detection_pin_state state;

    state.pin.pin_1 = digitalRead(DETECTION_PINS.pin_1);
    state.pin.pin_2 = digitalRead(DETECTION_PINS.pin_2);
    state.pin.pin_3 = digitalRead(DETECTION_PINS.pin_3);
    state.pin.pin_4 = digitalRead(DETECTION_PINS.pin_4);
    state.pin.pin_5 = digitalRead(DETECTION_PINS.pin_5);
    state.pin.__unused = 0;

    return state;
}


int is_hat_connected(union detection_pin_state *signature)
{
    return read_detection_pins().value == signature->value;
}
