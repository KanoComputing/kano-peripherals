# init_flow.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# TODO: Description


from kano.logging import logger

from kano_peripherals.wrappers.led_ring.base_animation import BaseAnimation
from kano_peripherals.return_codes import *

# TODO: Move these
from kano_peripherals.speaker_leds.colours import LED_MAGENTA, LED_RED, \
    LED_BLACK, LED_KANO_ORANGE


class InitFlow(BaseAnimation):
    """
    """

    LOCK_PRIORITY = 1

    def __init__(self):
        super(InitFlow, self).__init__()

    def start(self, duration, cycles):
        """
        """
        if not self.iface and not self.connect():
            logger.error('LED Ring: InitFlow: Could not aquire dbus interface!')
            return RC_FAILED_ANIM_GET_DBUS

        locked = self.iface.lock(self.LOCK_PRIORITY)
        if not locked:
            logger.error('LED Ring: InitFlow: Could not lock dbus interface!')
            return RC_FAILED_LOCKING_API

        vf = self.rotate(self.colour_wheel, cycles)
        vf2 = self.pulse(vf)
        self.animate(vf2, duration, 1.0, update_rate=0.005)

        if not self.iface.unlock():
            logger.warn('LED Ring: InitFlow: Could not unlock dbus interface!')

    def stop(self):
        """
        """
        super(InitFlow, self).stop('init-flow')
