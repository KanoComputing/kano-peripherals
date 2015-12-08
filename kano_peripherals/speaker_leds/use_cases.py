# use_cases.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#


# import os
import json

from kano_peripherals.speaker_leds.driver import high_level
from kano_peripherals.speaker_leds.colours import LED_RED, LED_MAGENTA, \
    LED_BLACK, LED_KANO_ORANGE


def notification_start(spec):
    speakerleds_iface, HW = high_level.get_speakerleds_interface()

    colours1, colours2 = _get_notification_colours(spec, HW)
    # _stop_all()
    # _detect_or_exit(True)
    vf = high_level.pulse(high_level.constant(colours1),
                          high_level.constant(colours2))
    high_level.animate(vf, 20, 10, update_rate=0.005)


def notification_stop():
    # _stop_all()
    pass


def initflow_pattern_start(duration, cycles):
    # _stop_all()
    # _detect_or_exit(True)
    vf = high_level.rotate(high_level.colourWheel, cycles)
    vf2 = high_level.pulse(vf)
    high_level.animate(vf2, duration, 1.0, update_rate=0.005)


def leds_off():
    speakerleds_iface, HW = high_level.get_speakerleds_interface()
    # _detect_or_exit(False)
    # _stop_all()
    speakerleds_iface.set_leds_off()


def detect():
    speakerleds_iface, HW = high_level.get_speakerleds_interface()
    return 1 if speakerleds_iface.detect() else 0


def _get_notification_colours(spec, HW):
    # defaults:
    if HW['QUANTIZE']:
        default_colour1 = LED_RED
    else:
        default_colour1 = LED_KANO_ORANGE
    default_colour2 = LED_BLACK

    colours1 = [default_colour1] * HW['NUM_LEDS']
    colours2 = [default_colour2] * HW['NUM_LEDS']

    try:
        j = json.loads(spec[0])
        if 'led_colours1' in j:
            colours1 = _validate_colours(j['led_colours1'], HW)
        if 'led_colours2' in j:
            colours2 = _validate_colours(j['led_colours2'], HW)

        if 'led_colours1' not in j and 'led_colours2' not in j:
            # no colours in spec, so adopt heuristic
            if j['title'] == "Kano World":
                colours1 = [LED_MAGENTA] * HW['NUM_LEDS']
    except:
        pass  # TODO: logger here instead
        # low_level.logger().error("failed to decode colour spec {}".format(spec))

    return (colours1, colours2)


def _validate_colours(colours, HW):
    """
    Make sure colours is a list of 10 valid colors.
    Allow an exception to be raised if we can't do this.
    """

    if len(colours) == 1:
        colours = [_validate_colour(colours[0])] * HW['NUM_LEDS']
    elif len(colours) < HW['NUM_LEDS']:
        raise "not enough colours"
    else:
        colours = map(_validate_colour, colours[:HW['NUM_LEDS']])
    return colours


def _validate_colour(colour):
    """
    Make sure colour is a tuple of floats.
    Allow an exception to be raised if it isn't.
    """
    return (float(colour[0]), float(colour[1]), float(colour[2]))


# def _detect_or_exit(check):  # TODO: move this to daemon
#     if detect() == 0:

#         # For now, we always reset the chip here, but later we may
#         # want to only do this once to avoid glitching
#         speakerleds_iface.setup(check)
#         return
#     else:
#         exit(1)


# def _stop_all():  # TODO: move this to daemon
#     """
#     Stop all animations.
#     Currently assumes all animations are run by kano-speakerleds, which
#     won't be correct eventually.
#     """
#     os.system('pkill --signal INT -f "kano-speakerleds notification"')
