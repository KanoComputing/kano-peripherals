# detection.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# TODO: Description.


import time

from kano_pi_hat.ck2_pro_hat import CK2ProHat

from kano.logging import logger


def power_button_cb1():
    logger.info('CK2ProHatService: _interrupt_thread: power_button_cb1: Called!')


def power_button_cb2():
    logger.info('CK2ProHatService: _interrupt_thread: power_button_cb2: Called!')


def low_battery_cb1():
    logger.info('CK2ProHatService: _interrupt_thread: low_battery_cb1: Called!')


def low_battery_cb2():
    logger.info('CK2ProHatService: _interrupt_thread: low_battery_cb2: Called!')


def main():
    ck2_pro_hat = CK2ProHat()
    ck2_pro_hat.initialise()

    if ck2_pro_hat.is_connected():
        logger.debug("main: PowerHat connected")

    ck2_pro_hat.register_power_off_cb(power_button_cb1)
    ck2_pro_hat.register_battery_level_changed_cb(low_battery_cb2)
    ck2_pro_hat.register_battery_level_changed_cb(low_battery_cb1)

    while True:
        time.sleep(10)


if __name__ == '__main__':
    main()
