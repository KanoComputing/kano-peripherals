#!/usr/bin/env python
#
# leds.py
#
# Copyright (C) 2017-2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Example for settings the LEDs for the LED hat
#

import paths

from kano_pi_hat.kano_hat_leds import KanoHatLeds


if __name__ == '__main__':
    LEDS = KanoHatLeds()

    LEDS.set_led(1, (0.5, 0.1, 1.0), show=False)
    LEDS.set_led(5, (1.0, 0.1, 1.0))
