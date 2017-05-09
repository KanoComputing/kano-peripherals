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
#include <signal.h>
#include <unistd.h>

#include "err.h"
#include "callbacks.h"
#include "battery.h"


// Tweak these values to clean battery state input
const unsigned int debounce_delay = 50000;  // microseconds
const unsigned int counter_threshold = 5;


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
    static bool prev_state = false;
    static unsigned int counter = 0;
    signal(SIGALRM, battery_level_changed);

    bool current_state = is_battery_low();

    if (current_state != prev_state) {
        counter = 0;
        prev_state = current_state;
        ualarm(debounce_delay, 0);

        return;
    }

    counter++;

    if (counter >= counter_threshold) {
        counter = 0;
        alarm(0);
        dispatch_cbs(battery_level_changed_cbs);
    } else {
        ualarm(debounce_delay, 0);
    }
}


int register_battery_level_changed_cb(void cb(void))
{
    if (initialise() != SUCCESS)
        return E_FAIL;

    add_cb(battery_level_changed_cbs, cb);
    wiringPiISR(LOW_BATTERY_PIN, INT_EDGE_BOTH, &battery_level_changed);
    return 0;
}
