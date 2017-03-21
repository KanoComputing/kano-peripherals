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


callback_list *hat_attached_cbs;
callback_list *hat_detached_cbs;


int initialise_detection()
{
    pullUpDnControl(DETECTION_PIN, DEFAULT_DETECTION_PIN_STATE);

    new_cb_list(&hat_attached_cbs);
    new_cb_list(&hat_detached_cbs);

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
        return false;
    } else {
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
