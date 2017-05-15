# base_animation.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The base class for an LED ring animation.
# Subclass this to create more animation routines.


import math
import time
import signal

from kano.utils import run_bg

# from kano_peripherals.speaker_leds.driver.high_level import get_speakerleds_interface
from kano_peripherals.pi_hat.driver.high_level import get_pihat_interface


class BaseAnimation(object):
    """
    It provides a set of high level animation functions which could be
    grouped to create different effects. It also abstracts which LED
    ring board it uses, either LED Speaker or Pi Hat.
    """

    def __init__(self):
        super(BaseAnimation, self).__init__()

        self.iface = None
        self.interrupted = False

        self.setup_signal_handler()

    def connect(self, retry_count=5):
        """
        Grab an interface to either the LED Speaker or Pi Hat
        depending on which one is plugged in.

        Returns:
            successful - bool whether was able to connect to a board
        """
        # self.iface = get_speakerleds_interface(retry_count=retry_count)
        # if self.iface and self.iface.detect():
        #     return True

        self.iface = get_pihat_interface(retry_count=retry_count)
        if self.iface and self.iface.detect():
            return True

        return False

    def setup_signal_handler(self):
        """
        Register a signal hander to listen for SIGINT to gracefully
        close the animation routine.
        """
        signal.signal(signal.SIGINT, self._signal_handler)

    def start(self):
        """
        Implement the animation loop here.
        """
        pass

    @staticmethod
    def stop(args):
        """
        Stop the animation loop and terminate process.

        Args:
            args - the animation id as expected from cmdline args
        """
        run_bg('pkill --signal INT -f "kano-speakerleds {}"'.format(args))

    def constant(self, values):
        """
        """
        def result_func(phase):
            return values
        return result_func

    def colour_wheel(self, hue, saturation=1.0, value=1.0):
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

    def rotate(self, value_func, phase_scale=1.0):
        """
        """
        num_leds = self.iface.get_num_leds()

        def result_func(phase):
            phase = phase * phase_scale
            values = list()

            for i in xrange(num_leds):
                values.append(value_func(math.modf(phase + float(i) / num_leds)[0]))

            return values
        return result_func

    def pulse(self, value_func, value_func2=None):
        """
        """
        num_leds = self.iface.get_num_leds()

        if value_func2 is None:
            value_func2 = self.constant([(0, 0, 0)] * num_leds)

        def mix_vals(a, b, m, n):
            (r1, g1, b1) = a
            (r2, g2, b2) = b
            return (r1 * m + r2 * n,
                    g1 * m + g2 * n,
                    b1 * m + b2 * n)

        def result_func(phase):
            values_t = value_func(phase)
            values2_t = value_func2(phase)

            # given phase in interval [0, 1)
            t = 2.0 * phase - 1  # in interval (-1, 1)
            m = 1.0 - t * t      # a concave function between 0 and 1 (the middle of t is 1)
            n = 1.0 - m          # a convexe function between 0 and 1 (m flipped)

            mixed_values = list()
            for i in xrange(num_leds):
                mixed_values.append(mix_vals(values_t[i], values2_t[i], m, n))

            return mixed_values

        return result_func

    def pulse_each(self, value_func, led_speeds, value_func2=None):
        """
        """
        num_leds = self.iface.get_num_leds()

        if value_func2 is None:
            value_func2 = self.constant([(0, 0, 0) for i in range(num_leds)])

        def mix_vals(a, b, m, n):
            (r1, g1, b1) = a
            (r2, g2, b2) = b
            return (r1 * m + r2 * n,
                    g1 * m + g2 * n,
                    b1 * m + b2 * n)

        def result_func(phase):
            values_t = value_func(phase)
            values2_t = value_func2(phase)

            mixed_values = list()

            for i in xrange(num_leds):
                # given phase in interval [0, 1)
                phase_each = phase * led_speeds[i] % 1  # create more cycles for this LED

                t = 2.0 * phase_each - 1  # in interval (-1, 1)
                m = 1.0 - t * t           # a concave function between 0 and 1
                n = 1.0 - m               # a convexe function between 0 and 1

                mixed_values.append(mix_vals(values_t[i], values2_t[i], m, n))

            return mixed_values

        return result_func

    def animate(self, value_function, duration, cycles, update_rate=(1.0 / 25.0), mask=None):
        """
        """
        successful = True

        start = time.time()
        if duration is None:
            duration = 365 * 24 * 60 * 60

        end = start + duration

        now = start
        while now < end and successful and not self.interrupted:
            # number of cycles passed of total
            phase = (now - start) * cycles / duration

            # get the fractional and integer parts
            (frac, rest) = math.modf(phase)

            # frac is a float in interval [0, 1), cyclic, and monotonically increasing
            leds = value_function(frac)

            successful = self.iface.set_all_leds(leds)

            time.sleep(update_rate)
            now = time.time()  # seconds since the epoch as float

        if self.iface:
            self.iface.set_leds_off()

        return successful

    def _signal_handler(self, signum, frame):
        self.interrupted = True
        if self.iface:
            self.iface.set_leds_off()
            self.iface.unlock()
