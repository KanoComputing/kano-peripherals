# init_flow.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Rainbow animation that runs on either the Pi Hat or the LED Speaker.
# The pattern is specific to the onboarding flow into the OS.


from kano.logging import logger

from kano_peripherals.wrappers.led_ring.base_animation import BaseAnimation
from kano_peripherals.return_codes import *

# TODO: Move these
from kano_peripherals.speaker_leds.colours import LED_MAGENTA, LED_RED, \
    LED_BLACK, LED_KANO_ORANGE


class InitFlow(BaseAnimation):
    """
    The onboarding animation pattern for an LED ring board.
    This is a wrapper over Pi Hat and LED Speaker.
    """

    LOCK_PRIORITY = 1

    def __init__(self):
        super(InitFlow, self).__init__()

    def start(self, duration, cycles):
        """
        Start the animation loop.

        Args:
            duration - int duration in seconds of animation
            cycles - int number of colour wheel spins during animation

        Returns:
            rc - int value with return code or None if no errors occured
        """

        # Connect to the DBus interface of a board with an LED ring.
        if not self.connect():
            logger.error('LED Ring: InitFlow: Could not aquire dbus interface!')
            return RC_FAILED_ANIM_GET_DBUS

        # Lock the API so anything below doesn't override our calls.
        locked = self.iface.lock(self.LOCK_PRIORITY)
        if not locked:
            logger.error('LED Ring: InitFlow: Could not lock dbus interface!')
            return RC_FAILED_LOCKING_API

        # Setup the animation parameters and run the loop.
        vf = self.rotate(self.colour_wheel, cycles)
        vf2 = self.pulse(vf)
        self.animate(vf2, duration, 1.0, update_rate=0.005)

    @staticmethod
    def stop():
        """
        Stop the animation loop and terminate process.
        """
        super(InitFlow, InitFlow).stop('init-flow')
