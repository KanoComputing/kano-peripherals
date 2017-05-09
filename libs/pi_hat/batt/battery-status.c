/**
 *
 * battery-status
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Tool to detect if the battery is connected and the charge is too low.
 * Exit code is 1 when this is the case.
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <err.h>

#include <ck2_pro_hat/ck2_pro_hat.h>


int main(int argc, char **argv)
{

    // TODO: flag to disable the lock file
    if (initialise_ck2_lite() != SUCCESS) {
        printf("could not initialize lite board\n");
    }

    if (initialise_ck2_pro() != SUCCESS) {
        printf("could not initialize pro board\n");
    }

    bool connected = is_ck2_pro_connected();
    printf("is battery connected? %s\n", (connected ? "yes" : "no"));

    bool low = is_battery_low();
    printf("is battery low? %s\n", (low ? "yes" : "no"));

    clean_up_ck2_pro();
    exit( connected && low );
}
