/**
 *
 * battery.c
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Core functions related to detecting the battery level
 *
 */


#include <stdbool.h>

#include "err.h"
#include "callbacks.h"
#include "battery.h"


callback_list *battery_level_changed_cbs;


int initialise_battery()
{
    new_cb_list(&battery_level_changed_cbs);
}


int clean_up_battery()
{
    free_cb_list(&battery_level_changed_cbs);

    return SUCCESS;
}


bool is_battery_low(void)
{
    return digitalRead(LOW_BATTERY_PIN) == LOW_BATTERY_TRIGGER_VALUE;
}


void battery_level_changed(void)
{
    // TODO: Debounce input
    dispatch_cbs(battery_level_changed_cbs);
}


int register_battery_level_changed_cb(void cb(void))
{
    if (initialise() != SUCCESS)
        return E_FAIL;

    add_cb(battery_level_changed_cbs, cb);
    wiringPiISR(LOW_BATTERY_PIN, INT_EDGE_BOTH, &battery_level_changed);
    return 0;
}
