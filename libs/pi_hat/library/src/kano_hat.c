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
#include "lock.h"
#include "power_button.h"


int initialise(void)
{
    switch (get_lock()) {
    case E_COULD_NOT_GET_LOCK:
        perror("Library is already in use");
        return E_LIBRARY_INITIALISED_ELSEWHERE;
    case E_ALREADY_INITIALISED:
        return SUCCESS;
    }

#ifdef USERSPACE
    wiringPiSetupSys();
#else
    wiringPiSetupGpio();
#endif

    initialise_power_button();
    initialise_detection();

    return SUCCESS;
}


int clean_up(void)
{
    clean_up_detection();
    release_lock();
}
