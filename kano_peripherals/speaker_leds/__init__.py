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


def validate_colour(colour):
    """
    Make sure colour is a tuple of floats.
    Allow an exception to be raised if it isn't.
    """

    return (float(colour[0]), float(colour[1]), float(colour[2]))


def validate_colours(colours):
    """
       Make sure colours is a list of 10 valid colors.
       Allow an exception to be raised if we can't do this.
    """

    if len(colours) == 1:
        colours = [validate_colour(colours[0])] * low_level.NUM_LEDS
    elif len(colours) < low_level.NUM_LEDS:
        raise "not enough colours"
    else:
        colours = map(validate_colour, colours[:low_level.NUM_LEDS])
    return colours

LED_BLACK =   (0.0, 0.0, 0.0)
LED_RED =     (1.0, 0.0, 0.0)
LED_GREEN =   (0.0, 1.0, 0.0)
LED_BLUE =    (0.0, 0.0, 1.0)
LED_YELLOW =  (1.0, 1.0, 0.0)
LED_CYAN =    (0.0, 1.0, 1.0)
LED_MAGENTA = (1.0, 0.0, 1.0)

LED_KANO_ORANGE = (1.0, 0x84/256.0, 0x2A/256.0)


def get_notification_colours(spec):

    # defaults:
    if low_level.QUANTIZE:
        default_colour1 = LED_RED
    else:
        default_colour1 = LED_KANO_ORANGE
    default_colour2 = LED_BLACK

    colours1 = [default_colour1] * low_level.NUM_LEDS
    colours2 = [default_colour2] * low_level.NUM_LEDS

    try:
        j = json.loads(spec[0])
        if 'led_colours1' in j:
            colours1 = validate_colours(j['led_colours1'])
        if 'led_colours2' in j:
            colours2 = validate_colours(j['led_colours2'])

        if 'led_colours1' not in j and  'led_colours2' not in j:
            # no colours in spec, so adopt heuristic
            if j['title'] == "Kano World":
                colours1 = [LED_MAGENTA] * low_level.NUM_LEDS
    except:
        low_level.logger().error("failed to decode colour spec {}".format(spec))

    return (colours1, colours2)


def notification_start(spec):
    detect_or_exit()
    stop_all()
    colours1, colours2 = get_notification_colours(spec)

    vf = high_level.pulse(colours1, colours2)
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
