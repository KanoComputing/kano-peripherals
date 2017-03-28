#!/usr/bin/env python

import time

import paths
from kano_pi_hat.kano_hat import KanoHat


def power_pressed():
    print 'Power button pressed'


if __name__ == '__main__':
    kano_hat = KanoHat()
    kano_hat.initialise()


    print "Hat is connected:", kano_hat.is_connected()
    kano_hat.register_power_off_cb(power_pressed)

    while True:
        time.sleep(1)
