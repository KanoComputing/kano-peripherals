/**
 *
 * main.c
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Sample usage of the Kano Pi Hat library
 *
 */


#include <stdio.h>
#include <unistd.h>

#include "setup.h"
#include "ck2_pro_hat/ck2_pro_hat.h"


void power_button_pressed(void)
{
    fprintf(stderr, "Power button pressed [ 1 ]\n");
}

void power_button_pressed2(void)
{
    fprintf(stderr, "Power button pressed [ 2 ]\n");
}

void low_battery(void)
{
    fprintf(stderr, "Low battery [ 1 ]\n");
}

void low_battery2(void)
{
    fprintf(stderr, "Low battery [ 2 ]\n");
}


int main(int argc, char **argv)
{
    initialise_ck2_pro();

    if (is_ck2_pro_connected()) {
        fprintf(stderr, "PowerHat is connected\n");
    } else {
        fprintf(stderr, "PowerHat is not connected\n");
    }

    register_power_off_cb(&power_button_pressed);
    register_battery_level_changed_cb(&low_battery);
    register_battery_level_changed_cb(&low_battery2);

    for (;;) {
        sleep(10);
    }

    clean_up();
    clean_up_ck2_pro();

    return 0;
}
