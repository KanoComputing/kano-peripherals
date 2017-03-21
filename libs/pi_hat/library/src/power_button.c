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


#include <time.h>
#include <stdio.h>
#include <wiringPi.h>

#include "power_button.h"
#include "callbacks.h"
#include "err.h"
#include "pins.h"


const int button_timeout = 5;
callback_list *power_button_cbs;


int initialise_power_button()
{
    pullUpDnControl(POWER_PIN, DEFAULT_POWER_PIN_STATE);
    new_cb_list(&power_button_cbs);

    return SUCCESS;
}


int clean_up_power_button()
{
    free_cb_list(&power_button_cbs);

    return SUCCESS;
}


void press(void)
{
    static time_t last_call = 0;
    const time_t current_time = time(NULL);

    if (current_time - last_call > button_timeout) {
        last_call = current_time;
        dispatch_cbs(power_button_cbs);
    }
}


int register_power_off_cb(void cb(void))
{
    if (initialise() != SUCCESS)
        return E_FAIL;

    add_cb(power_button_cbs, cb);
    wiringPiISR(POWER_PIN, INT_EDGE_RISING, &press);

    return 0;
}
