# speaker_leds/__init__.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

# ******* Commands for app integration *********

import low_level
import high_level
import os


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


def notification_start(colours):
    detect_or_exit()
    print colours
    if len(colours) == 0:
        colours1 = [(1.0, 0.27, 0.0)]
    else:
        colours1 = [tuple(map(float, colours[0]))]

    if len(colours) <= 1:
        colours2 = [(0, 0, 0)]
    else:
        colours2 = [tuple(map(float, colours[1]))]

    print colours1, colours2

    vf = high_level.pulse(colours1 * low_level.NUM_LEDS, colours2 * low_level.NUM_LEDS)
    high_level.animate(vf, 60*60, 60*60*2, updateRate=0.005)


def notification_stop():
    os.system('pkill --signal INT -f "kano-speakerleds notification"')


def initflow_pattern_start():
    detect_or_exit()
    vf = high_level.rotate(high_level.colourWheel)
    high_level.animate(vf, 60*60, 60*60*2, updateRate=0.005)


def initflow_pattern_stop():
    os.system('pkill --signal INT -f "kano-speakerleds initflow"')


def all_off():
    detect_or_exit()
