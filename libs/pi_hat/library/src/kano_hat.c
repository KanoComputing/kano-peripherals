/**
 *
 * kano_hat.c
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Hat interaction library
 *
 */


#include <wiringPi.h>
#include <stdbool.h>
#include <unistd.h>

#include "kano_hat.h"
#include "err.h"
#include "power_button.h"


int initialise(void)
{
    static bool is_initialised = false;

    if (is_initialised)
        return SUCCESS;

#ifdef USERSPACE
    wiringPiSetupSys();
#else
    wiringPiSetupGpio();
#endif

    initialise_power_button();
    initialise_detection();

    is_initialised = true;

    return SUCCESS;
}


int clean_up(void)
{
    clean_up_detection();
}
