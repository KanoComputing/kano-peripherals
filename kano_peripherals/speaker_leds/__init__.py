# speaker_leds/__init__.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

# ******* Commands for app integration *********

import low_level
import high_level
import os
import json


def detect():
    if low_level.detect():
        return 0
    else:
        return 1


def detect_or_exit():
    if detect() == 0:

        # For now, we always reset the chip here, but later we may
        # want to only do this once to avoid glitching
        low_level.setup()
        return
    else:
        exit(1)


def stop_all():
    """
    Stop all animations.
    Currently assumes all animations are run by kano-speakerleds, which
    won't be correct eventually.
    """
    os.system('pkill --signal INT -f "kano-speakerleds notification"')


def get_notification_colours(spec):

    # defaults:
    colours1 = [(1.0, 0.27, 0.0)] * low_level.NUM_LEDS
    colours2 = [(0, 0, 0)] * low_level.NUM_LEDS

    return (colours1, colours2)


def notification_start(spec):
    detect_or_exit()
    stop_all()
    colours1, colours2 = get_notification_colours(spec)

    vf = high_level.pulse(colours1, colours2 * low_level.NUM_LEDS)
    high_level.animate(vf, 60*60, 60*60*2, updateRate=0.005)


def notification_stop():
    stop_all()


def initflow_pattern_start():
    detect_or_exit()
    stop_all()
    vf = high_level.rotate(high_level.colourWheel)
    high_level.animate(vf, 60*60, 60*60*2, updateRate=0.005)


def initflow_pattern_stop():
    os.system('pkill --signal INT -f "kano-speakerleds initflow"')


def all_off():
    detect_or_exit()
    stop_all()
