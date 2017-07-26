/**
 *
 * setup.c
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Main setup functions of the library
 *
 */


#include <stdbool.h>
#include <unistd.h>
#include <stdio.h>

#include <wiringPi.h>

#include "setup.h"
#include "err.h"
#include "lock.h"
#include "power_button.h"


// TODO: Create an initialisation flag for this "module"

int initialise(void)
{
    switch (get_lock()) {
    case E_COULD_NOT_GET_LOCK:
        perror("Library is already in use");
        return E_LIBRARY_INITIALISED_ELSEWHERE;
    case E_ALREADY_INITIALISED:
        printf("Don't need to init, already done\n");
        return SUCCESS;
    }

    static bool is_setup = false;

    if (!is_setup) {
#ifdef USERSPACE
        wiringPiSetupSys();
#else
        wiringPiSetupGpio();
#endif
        is_setup = true;
    }

    initialise_detection();
    initialise_power_button();

    return SUCCESS;
}


int clean_up(void)
{
    clean_up_detection();
    clean_up_power_button();
    release_lock();
}
