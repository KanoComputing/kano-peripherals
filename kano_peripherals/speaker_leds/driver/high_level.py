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
import dbus.exceptions
import signal

from kano.logging import logger

from kano_peripherals.paths import BUS_NAME, SPEAKER_LEDS_OBJECT_PATH, SPEAKER_LEDS_IFACE


# catch signals to allow clean exit
interrupted = False


def setup_signal_handler():
    signal.signal(signal.SIGINT, signal_handler)


def signal_handler(signal, frame):
    global interrupted
    interrupted = True

    speakerleds_iface = get_speakerleds_interface()
    if not speakerleds_iface:
        return

    speakerleds_iface.unlock()


def get_speakerleds_interface():
    try:
        return dbus.Interface(
            dbus.SessionBus().get_object(BUS_NAME, SPEAKER_LEDS_OBJECT_PATH),
            SPEAKER_LEDS_IFACE
        )
    except dbus.exceptions.DBusException:
        logger.warn('LED Speaker DBus not found. Is kano-boards-daemon running?')
    except Exception as e:
        logger.error('Something unexpected occured in get_speakerleds_interface - [{}]'
                     .format(e))


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
    speakerleds_iface = get_speakerleds_interface()
    if not speakerleds_iface:
        return

    num_leds = speakerleds_iface.get_num_leds()

    def resultFunc(phase):
        phase = phase * phase_scale
        values = list()

        for i in xrange(num_leds):
            values.append(valueFunc(math.modf(phase + float(i) / num_leds)[0]))

        return values
    return resultFunc


def pulse(valueFunc, valueFunc2=None):
    """
    """
    speakerleds_iface = get_speakerleds_interface()
    if not speakerleds_iface:
        return

    num_leds = speakerleds_iface.get_num_leds()

    if valueFunc2 is None:
        valueFunc2 = constant([(0, 0, 0)] * num_leds)

    def mix_vals(a, b, m, n):
        (r1, g1, b1) = a
        (r2, g2, b2) = b
        return (r1 * m + r2 * n,
                g1 * m + g2 * n,
                b1 * m + b2 * n)

    def resultFunc(phase):
        values_t = valueFunc(phase)
        values2_t = valueFunc2(phase)

        # given phase in interval [0, 1)
        t = 2.0 * phase - 1  # in interval (-1, 1)
        m = 1.0 - t * t      # a concave function between 0 and 1 (the middle of t is 1)
        n = 1.0 - m          # a convexe function between 0 and 1 (m flipped)

        mixed_values = list()
        for i in xrange(num_leds):
            mixed_values.append(mix_vals(values_t[i], values2_t[i], m, n))

        return mixed_values

    return resultFunc


def pulse_each(valueFunc, led_speeds, valueFunc2=None):
    """
    """
    speakerleds_iface = get_speakerleds_interface()
    if not speakerleds_iface:
        return

    num_leds = speakerleds_iface.get_num_leds()

    if valueFunc2 is None:
        valueFunc2 = constant([(0, 0, 0) for i in range(num_leds)])

    def mix_vals(a, b, m, n):
        (r1, g1, b1) = a
        (r2, g2, b2) = b
        return (r1 * m + r2 * n,
                g1 * m + g2 * n,
                b1 * m + b2 * n)

    def resultFunc(phase):
        values_t = valueFunc(phase)
        values2_t = valueFunc2(phase)

        mixed_values = list()

        for i in xrange(num_leds):
            # given phase in interval [0, 1)
            phase_each = phase * led_speeds[i] % 1  # create more cycles for this LED

            t = 2.0 * phase_each - 1  # in interval (-1, 1)
            m = 1.0 - t * t           # a concave function between 0 and 1
            n = 1.0 - m               # a convexe function between 0 and 1

            mixed_values.append(mix_vals(values_t[i], values2_t[i], m, n))

        return mixed_values

    return resultFunc


def animate(valueFunction, duration, cycles, update_rate=0.02, mask=None):
    """
    """
    setup_signal_handler()

    speakerleds_iface = get_speakerleds_interface()
    if not speakerleds_iface:
        return False

    successful = True

    start = time.time()
    if duration is None:
        duration = 365 * 24 * 60 * 60

    end = start + duration

    now = start
    while now < end and successful and not interrupted:
        # number of cycles passed of total
        phase = (now - start) * cycles / duration

        # get the fractional and integer parts
        (frac, rest) = math.modf(phase)

        # frac is a float in interval [0, 1), cyclic, and monotonically increasing
        leds = valueFunction(frac)

        successful = speakerleds_iface.set_all_leds(leds)

        time.sleep(update_rate)
        now = time.time()  # seconds since the epoch as float

    speakerleds_iface.set_leds_off()

    return successful
