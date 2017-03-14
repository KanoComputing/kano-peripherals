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

#include "kano_hat.h"


void power_button_pressed(void)
{
    printf("Power button pressed\n");
}


void hat_plugged_in(void)
{
    printf("Hat plugged in\n");
}

void hat_unplugged(void)
{
    printf("Hat unplugged\n");
}



int main(int argc, char **argv)
{
    initialise();

    register_power_off_cb(&power_button_pressed);
    register_hat_attached_cb(&hat_plugged_in);
    register_hat_detached_cb(&hat_unplugged);

    for (;;) {
        sleep(10);
    }

    clean_up();

    return 0;
}
