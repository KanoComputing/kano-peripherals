# speaker_leds/__init__.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

# ******* Commands for app integration *********

import low_level


def detect():
    if low_level.detect():
        return 0
    else:
        return 1


def detect_or_exit():
    if low_level.detect():

        # For now, we always reset the chip here, but later we may
        # want to only do this once to avoid glitching
        low_level.setup()
        return
    else:
        exit(1)


def notification_start():
    detect_or_exit()
    low_level.test1()


def notification_stop():
    detect_or_exit()


def initflow_pattern():
    detect_or_exit()


def all_off():
    detect_or_exit()
