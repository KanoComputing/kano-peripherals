/**
 *
 * setup.h
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Main setup functions of the common library
 *
 */


#ifndef __SETUP_H__
#define __SETUP_H__


#include <wiringPi.h>

#include "err.h"
#include "callbacks.h"
#include "lock.h"
#include "power_button.h"
#include "pins.h"


int initialise(void);
int clean_up(void);


#endif  // __SETUP_H__
