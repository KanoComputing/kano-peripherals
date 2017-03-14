#!/usr/bin/env python

import paths

from kano_pi_hat.kano_hat_leds import KanoHatLeds


if __name__ == '__main__':
    LEDS = KanoHatLeds()

    LEDS.set_led(1, (0.5, 0.1, 1.0), show=False)
    LEDS.set_led(5, (1.0, 0.1, 1.0))
