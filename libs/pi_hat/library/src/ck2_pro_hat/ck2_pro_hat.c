/**
 *
 * ck2_pro_hat.c
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * CK2 Pro hat interaction library
 *
 */


#include "ck2_pro_hat/ck2_pro_hat.h"
#include "ck2_pro_hat/pins.h"
#include "setup.h"
#include "detection.h"
#include "battery.h"
#include "err.h"


int initialise_ck2_pro(void)
{
    const int rc = initialise();
    if (rc != SUCCESS) {
        return rc;
    }

    if (!is_ck2_pro_connected()) {
        return E_HAT_NOT_ATTACHED;
    }

    // Traditionally done on init
    initialise_battery();

    return SUCCESS;
}


void clean_up_ck2_pro(void)
{
    clean_up_battery();
    clean_up();
}


bool is_ck2_pro_connected(void)
{
    return is_hat_connected(&CK2_PRO_DETECTION_SIGNATURE);
}
