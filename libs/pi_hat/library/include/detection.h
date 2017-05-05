/**
 *
 * detection.h
 *
 * Copyright (C) 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Hat detection and connectivity functions
 *
 */


#ifndef __DETECTION_H__
#define __DETECTION_H__


struct pins {
    unsigned char __unused: 3;
    unsigned char pin_1: 1;
    unsigned char pin_2: 1;
    unsigned char pin_3: 1;
    unsigned char pin_4: 1;
    unsigned char pin_5: 1;
};

struct detection_pins {
    const unsigned char pin_1;
    const unsigned char pin_2;
    const unsigned char pin_3;
    const unsigned char pin_4;
    const unsigned char pin_5;
};

union detection_pin_state {
    struct pins pin;
    unsigned char value;
};


/**
 * Selection of pins to use for the detection
 * NB: Pin 5 defaults to HIGH, while the other pins default LOW. This means that
 *     the signature for no hat attached is 0b00001 (not 0b00000)
 *
 */
static const struct detection_pins DETECTION_PINS = {
    .pin_1 = 22,  // Physical 15, BCM 22
    .pin_2 = 23,  // Physical 16, BCM 23
    .pin_3 = 24,  // Physical 18, BCM 24
    .pin_4 = 27,  // Physical 13, BCM 27
    /**
     * Special pin which is the only pin actvely grounded on the Lite board
     * Defaults to HIGH
     */
    .pin_5 = 26,  // Physical 37, BCM 26
};


int initialise_detection();
int clean_up_detection();
int is_hat_connected(union detection_pin_state *signature);


#endif  // __DETECTION_H__
