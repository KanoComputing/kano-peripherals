#!/usr/bin/env python
#
# power_button.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# Interfacing with the power button through the raw library
#

import time

import paths
from kano_pi_hat.kano_hat import KanoHat


def power_pressed_cb():
    print 'Power button pressed'


if __name__ == '__main__':
    kano_hat = KanoHat()
    kano_hat.initialise()


    print "Hat is connected:", kano_hat.is_connected()
    kano_hat.register_power_off_cb(power_pressed_cb)

    while True:
        time.sleep(1)
