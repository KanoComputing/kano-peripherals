# high_level.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Low level programming of the LED chip. Also includes linerarity adjustment.
# Setup of the chip useds pwm_driver.py, but led programming does not go
# via that file to avoid overhead.


import time
import math
import dbus
import signal

from kano_peripherals.paths import BUS_NAME, SPEAKER_LEDS_OBJECT_PATH, SPEAKER_LEDS_IFACE


# catch signals to allow clean exit
interrupted = False


def signal_handler(signal, frame):
    global interrupted
    interrupted = True

signal.signal(signal.SIGINT, signal_handler)


def get_speakerleds_interface():
    speakerleds_iface = dbus.Interface(
        dbus.SessionBus().get_object(BUS_NAME, SPEAKER_LEDS_OBJECT_PATH),
        SPEAKER_LEDS_IFACE
    )
    HW = speakerleds_iface.get_data()

    return speakerleds_iface, HW


def constant(values):
    """
    """

    def resultFunc(phase):
        return values
    return resultFunc


def colourWheel(hue, saturation=1.0, value=1.0):
    """
    HSL Colour Wheel representation
    """

    (frac, whole) = math.modf(hue * 6)

    p = value * (1 - saturation)
    q = value * (1 - saturation * frac)
    t = value * (1 - saturation * (1 - frac))

    if whole == 0:
        return (value, t, p)
    elif whole == 1:
        return (q, value, p)
    elif whole == 2:
        return (p, value, t)
    elif whole == 3:
        return (p, q, value)
    elif whole == 4:
        return (t, p, value)
    elif whole == 5:
        return (value, p, q)


def rotate(valueFunc, phase_scale=1.0):
    """
    """
    speakerleds_iface, HW = get_speakerleds_interface()

    def resultFunc(phase):
        phase = phase * phase_scale
        values = list()

        for i in xrange(HW['NUM_LEDS']):
            values.append(valueFunc(math.modf(phase + float(i) / HW['NUM_LEDS'])[0]))

        return values
    return resultFunc


def pulse(values, values2=None):
    """
    """
    speakerleds_iface, HW = get_speakerleds_interface()

    if values2 is None:
        values2 = constant([(0, 0, 0)] * HW['NUM_LEDS'])

    def mix_vals(a, b, m, n):
        (r1, g1, b1) = a
        (r2, g2, b2) = b
        return (r1 * m + r2 * n,
                g1 * m + g2 * n,
                b1 * m + b2 * n)

    def resultFunc(phase):
        values_t = values(phase)
        values2_t = values2(phase)

        t = 2.0 * phase - 1
        m = 1.0 - t * t
        n = 1.0 - m

        mixed_values = list()
        for i in xrange(HW['NUM_LEDS']):
            mixed_values.append(mix_vals(values_t[i], values2_t[i], m, n))

        return mixed_values

    return resultFunc


def animate(valueFunction, duration, cycles, update_rate=0.02, mask=None):
    """
    """
    speakerleds_iface, HW = get_speakerleds_interface()

    start = time.time()
    if duration is None:
        duration = 365 * 24 * 60 * 60

    end = start + duration

    now = start
    while now < end and not interrupted:
        phase = (now - start) * cycles / duration

        (frac, rest) = math.modf(phase)

        leds = valueFunction(frac)

        speakerleds_iface.set_all_leds(leds)

        time.sleep(update_rate)
        now = time.time()

    speakerleds_iface.set_leds_off()
