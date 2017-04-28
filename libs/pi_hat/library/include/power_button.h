/**
 *
 * power_button.h
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Power button interaction
 *
 */


#ifndef __POWER_BUTTON_H__
#define __POWER_BUTTON_H__


int initialise_power_button();
int clean_up_power_button();
int register_power_off_cb(void cb(void));


#endif  // __POWER_BUTTON_H__
