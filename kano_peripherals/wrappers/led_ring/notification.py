# notification.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Notification animation that runs on either the Pi Hat or the LED Speaker.


import json

from kano.logging import logger

from kano_peripherals.wrappers.led_ring.base_animation import BaseAnimation
from kano_peripherals.return_codes import *

# TODO: Move these
from kano_peripherals.speaker_leds.colours import LED_MAGENTA, LED_RED, LED_BLACK


class Notification(BaseAnimation):
    """
    The OS notification animation for an LED ring board.
    This is a wrapper over Pi Hat and LED Speaker.
    """

    LOCK_PRIORITY = 2

    def __init__(self):
        super(Notification, self).__init__()

    def start(self, spec):
        """
        Start the animation loop.

        Args:
            spec - json wrapped data with LED colours

        Returns:
            rc - int value with return code or None if no errors occured
        """

        # Connect to the DBus interface of a board with an LED ring.
        if not self.connect():
            logger.error('LED Ring: Notification: Could not aquire dbus interface!')
            return RC_FAILED_ANIM_GET_DBUS

        # Lock the API so anything below doesn't override our calls.
        locked = self.iface.lock(self.LOCK_PRIORITY)
        if not locked:
            logger.error('LED Ring: Notification: Could not lock dbus interface!')
            return RC_FAILED_LOCKING_API

        # Setup the animation parameters and run the loop.
        colours1, colours2 = self._get_notification_colours(spec, self.iface.get_num_leds())
        vf = self.pulse(self.constant(colours1), self.constant(colours2))
        self.animate(vf, 60 * 60, 60 * 60 / 2, update_rate=0.005)

    @staticmethod
    def stop():
        """
        Stop the animation loop and terminate process.
        """
        super(Notification, Notification).stop('notification')

    def _get_notification_colours(self, spec, num_leds):
        """ """

        default_colour1 = LED_RED
        default_colour2 = LED_BLACK

        colours1 = [default_colour1] * num_leds
        colours2 = [default_colour2] * num_leds

        try:
            j = json.loads(spec[0])
            if 'led_colours1' in j:
                colours1 = self._validate_colours(j['led_colours1'], num_leds)
            if 'led_colours2' in j:
                colours2 = self._validate_colours(j['led_colours2'], num_leds)

            if 'led_colours1' not in j and 'led_colours2' not in j:
                # no colours in spec, so adopt heuristic
                if j['title'] == "Kano World":
                    colours1 = [LED_MAGENTA] * num_leds
        except:
            logger.error("failed to decode colour spec {}".format(spec))

        return (colours1, colours2)

    def _validate_colours(self, colours, num_leds):
        """
        Make sure colours is a list of 10 valid colors.
        Allow an exception to be raised if we can't do this.
        """
        if len(colours) == 1:
            colours = [self._validate_colour(colours[0])] * num_leds
        elif len(colours) < num_leds:
            raise "not enough colours"
        else:
            colours = map(self._validate_colour, colours[:num_leds])
        return colours

    def _validate_colour(self, colour):
        """
        Make sure colour is a tuple of floats.
        Allow an exception to be raised if it isn't.
        """
        return (float(colour[0]), float(colour[1]), float(colour[2]))
