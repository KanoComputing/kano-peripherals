/**
 *
 * detection.c
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Hat detection and connectivity functions
 *
 */


#include <stdbool.h>
#include <wiringPi.h>

#include "callbacks.h"
#include "err.h"
#include "pins.h"


#define SND_MODULE "snd_bcm2835"
static bool hat_initialised = false;

callback_list *hat_attached_cbs;
callback_list *hat_detached_cbs;


void hat_init() {
    if (!hat_initialised) {
        system("kano-settings-cli set audio hdmi");
        hat_initialised = true;
    }
}


void hat_destroy() {
    if (hat_initialised) {
        hat_initialised = false;
    }
}


int initialise_detection()
{
    pullUpDnControl(DETECTION_PIN, DEFAULT_DETECTION_PIN_STATE);

    new_cb_list(&hat_attached_cbs);
    new_cb_list(&hat_detached_cbs);

    is_hat_connected();

    // The sound module was disabled at boot to avoid PiHat drivers from getting
    // desync'ed on the PWM pin. We enable it back as soon as possible.
    system("modprobe -i " SND_MODULE);

    return SUCCESS;
}


int clean_up_detection()
{
    free_cb_list(&hat_attached_cbs);
    free_cb_list(&hat_detached_cbs);

    return SUCCESS;
}


int is_hat_connected(void)
{
    if (digitalRead(DETECTION_PIN) == DEFAULT_DETECTION_PIN_VAL) {
        hat_destroy();
        return false;
    } else {
        hat_init();
        return true;
    }
}


void detect_hat_state(void)
{
    if (initialise() != SUCCESS)
        return;

    if (is_hat_connected()) {
        dispatch_cbs(hat_attached_cbs);
    } else {
        dispatch_cbs(hat_detached_cbs);
    }
}


int register_hat_attached_cb(void cb(void))
{
    if (initialise() != SUCCESS)
        return E_FAIL;

    add_cb(hat_attached_cbs, cb);
    wiringPiISR(DETECTION_PIN, INT_EDGE_BOTH, &detect_hat_state);
    return 0;
}


int register_hat_detached_cb(void cb(void))
{
    if (initialise() != SUCCESS)
        return E_FAIL;

    add_cb(hat_detached_cbs, cb);
    wiringPiISR(DETECTION_PIN, INT_EDGE_BOTH, &detect_hat_state);

    return 0;
}
