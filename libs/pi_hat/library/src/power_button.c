/**
 *
 * power_button.c
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Power button interaction
 *
 */


#include <wiringPi.h>

#include "power_button.h"
#include "err.h"
#include "pins.h"


int initialise_power_button()
{
    pullUpDnControl(POWER_PIN, DEFAULT_POWER_PIN_STATE);

    return SUCCESS;
}


int register_power_off_cb(void cb(void))
{
    if (initialise() != SUCCESS)
        return E_FAIL;

    wiringPiISR(POWER_PIN, INT_EDGE_RISING, cb);
    return 0;
}
