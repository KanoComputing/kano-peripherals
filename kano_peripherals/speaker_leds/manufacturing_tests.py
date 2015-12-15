# manufacturing_tests.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#


import time

from kano_peripherals.speaker_leds.driver import high_level
from kano_peripherals.speaker_leds.use_cases import _stop


def manufacturing_test_start(len1, len2, len3):
    speakerleds_iface = high_level.get_speakerleds_interface()
    if not speakerleds_iface:
        print 'LED Speaker dbus daemon not found. \n' \
              'Please run "kano-boards-daemon &" first and try again.'
        return

    num_leds = speakerleds_iface.get_num_leds()

    while not high_level.interrupted:
        try:
            speakerleds_iface.setup(False)
            _stop()
            high_level.setup_signal_handler()

            speakerleds_iface.set_all_leds([(1.0, 0.0, 0.0)] * num_leds)
            time.sleep(len1)
            speakerleds_iface.set_all_leds([(0.0, 1.0, 0.0)] * num_leds)
            time.sleep(len2)
            speakerleds_iface.set_all_leds([(0.0, 0.0, 1.0)] * num_leds)
            time.sleep(len3)
        except IOError:
            print "Waiting for speaker"
            time.sleep(1)
