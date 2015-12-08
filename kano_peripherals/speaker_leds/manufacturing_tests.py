# manufacturing_tests.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#


import time

from kano_peripherals.speaker_leds.driver import high_level


def manufacturing_test_start(len1, len2, len3):
    speakerleds_iface, HW = high_level.get_speakerleds_interface()

    while not high_level.interrupted:
        try:
            speakerleds_iface.setup(False)
            # stop_all()  TODO?
            speakerleds_iface.set_all_leds([(1.0, 0.0, 0.0)] * 10)
            time.sleep(len1)
            speakerleds_iface.set_all_leds([(0.0, 1.0, 0.0)] * 10)
            time.sleep(len2)
            speakerleds_iface.set_all_leds([(0.0, 0.0, 1.0)] * 10)
            time.sleep(len3)
        except IOError:
            print "Waiting for speaker"
            time.sleep(1)
