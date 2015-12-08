# __init__.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

__author__ = 'Kano Computing Ltd.'
__email__ = 'dev@kano.me'


# exporting methods used by the binary

from kano_peripherals.speaker_leds.use_cases import \
    detect, leds_off, \
    notification_start, notification_stop, \
    initflow_pattern_start

from kano_peripherals.speaker_leds.manufacturing_tests import \
    manufacturing_test_start
