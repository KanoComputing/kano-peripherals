# speaker_leds/low_level.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Low level programming of the LED chip. Also includes linerarity adjustment.
# Setup of the chip useds pwm_driver.py, but led programming does not go
# via that file to avoid overhead.

import low_level
import time
import math

import signal
import sys

# catch signals to allow clean exit
interrupted = False


def signal_handler(signal, frame):
    global interrupted
    interrupted = True

signal.signal(signal.SIGINT, signal_handler)



def animate(valueFunction, duration, cycles, updateRate=0.02, mask=None):
    start = time.time()
    if duration is None:
        duration = 365 * 24 * 60 * 60

    end = start+duration

    now = start
    while now < end and not interrupted:
        phase = (now - start) * cycles / duration

        (frac, rest) = math.modf(phase)

        leds = valueFunction(frac)

        low_level.setAllLeds(leds)

        time.sleep(updateRate)
        now = time.time()

    low_level.setLedsOff()


def pulse(values, values2=None):
    if values2 is None:
        values2 = [(0, 0, 0)] * low_level.NUM_LEDS

    def mix_vals(a, b, m, n):
        (r1, g1, b1) = a
        (r2, g2, b2) = b
        return (r1 * m + r2 * n,
                g1 * m + g2 * n,
                b1 * m + b2 * n)

    def resultFunc(phase):
        t = 2.0 * phase-1
        m = 1.0 - t * t
        n = 1.0 - m

        mixed_values = [mix_vals(values[i], values2[i], m, n) for i in xrange(low_level.NUM_LEDS)]

        return mixed_values

    return resultFunc


def colourWheel(h, s=1.0, v=1.0):
    (frac, whole) = math.modf(h * 6)

    p = v * (1 - s)
    q = v * (1 - s * frac)
    t = v * (1 - s * (1 - frac))

    if whole == 0:
        return (v, t, p)
    elif whole == 1:
        return (q, v, p)
    elif whole == 2:
        return (p, v, t)
    elif whole == 3:
        return (p, q, v)
    elif whole == 4:
        return (t, p, v)
    elif whole == 5:
        return (v, p, q)


def rotate(valueFunc):
    def resultFunc(phase):
        return [valueFunc(math.modf(phase + float(i)/low_level.NUM_LEDS)[0]) for i in xrange(low_level.NUM_LEDS)]
    return resultFunc
