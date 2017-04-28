/**
 *
 * battery.h
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Core functions related to detecting the battery level
 *
 */


#include <stdbool.h>

#include "pins.h"


int initialise_battery();
int clean_up_battery();
bool is_battery_low(void);
int register_battery_level_changed_cb(void cb(void));
