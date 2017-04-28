/**
 *
 * kano_hat.c
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * CK2 Lite hat interaction library
 *
 */


#include "ck2_lite_hat/ck2_lite_hat.h"
#include "ck2_lite_hat/pins.h"
#include "setup.h"
#include "detection.h"
#include "err.h"


#define SND_MODULE "snd_bcm2835"


int initialise_ck2_lite(void)
{
    initialise();
    initialise_detection();

    if (!is_ck2_lite_connected()) {
        return E_HAT_NOT_ATTACHED;
    }

    // The sound module was disabled at boot to avoid PiHat drivers from getting
    // desync'ed on the PWM pin. We enable it back as soon as possible.
    system("modprobe -i " SND_MODULE);

    // Traditionally done on init
    system("kano-settings-cli set audio hdmi");

    return SUCCESS;
}


void clean_up_ck2_lite(void)
{
}



bool is_ck2_lite_connected(void)
{
    return is_hat_connected(&CK2_LITE_DETECTION_SIGNATURE);
}
