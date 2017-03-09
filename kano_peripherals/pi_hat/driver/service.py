# service.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#


import os
import math
import dbus
import dbus.service

from gi.repository import GObject

from kano.logging import logger

from kano_peripherals.lockable_service import LockableService
from kano_peripherals.paths import PI_HAT_OBJECT_PATH, PI_HAT_IFACE


class PiHatService(dbus.service.Object):
    """
    This is a DBus Service provided by kano-boards-daemon.

    It exports an object to /me/kano/boards/PiHat and
    its interface to me.kano.boards.PiHat

    Does not require sudo.
    """

    # LED Speaker Hardware Spec
    NUM_LEDS = 10            # this is public

    # the top priority level for an api lock
    MAX_PRIORITY_LEVEL = 10  # this is public

    def __init__(self, bus_name):
        super(PiHatService, self).__init__(bus_name, PI_HAT_OBJECT_PATH)

        self.lockable_service = LockableService(max_priority=self.MAX_PRIORITY_LEVEL)
        self.is_plugged = False

    # --- Board Detection ---------------------------------------------------------------

    @dbus.service.method(PI_HAT_IFACE, in_signature='b', out_signature='')
    def setup(self, check):
        """ TBD
        """
        pass

    @dbus.service.method(PI_HAT_IFACE, in_signature='', out_signature='b')
    def detect(self):
        """ TBD
        """
        return False

    @dbus.service.method(PI_HAT_IFACE, in_signature='', out_signature='b')
    def is_plugged(self):
        """
        """
        return self.is_plugged

    # --- API Locking -------------------------------------------------------------------

    @dbus.service.method(PI_HAT_IFACE, in_signature='i', out_signature='s', sender_keyword='sender_id')
    def lock(self, priority, sender_id=None):
        """
        """
        return self.lockable_service.lock(priority, sender_id)

    @dbus.service.method(PI_HAT_IFACE, in_signature='', out_signature='b', sender_keyword='sender_id')
    def unlock(self, sender_id=None):
        """
        """
        return self.lockable_service.unlock(sender_id)

    @dbus.service.method(PI_HAT_IFACE, in_signature='i', out_signature='b')
    def is_locked(self, priority):
        """
        """
        return self.lockable_service.is_locked(priority)

    @dbus.service.method(PI_HAT_IFACE, in_signature='', out_signature='i')
    def get_max_lock_priority(self):
        """
        """
        return self.lockable_service.get_max_lock_priority()

    # --- LED Programming with Locked API -----------------------------------------------

    @dbus.service.method(PI_HAT_IFACE, in_signature='s', out_signature='b', sender_keyword='sender_id')
    def set_leds_off_with_token(self, token, sender_id=None):
        """
        """
        return False

    @dbus.service.method(PI_HAT_IFACE, in_signature='a(ddd)s', out_signature='b', sender_keyword='sender_id')
    def set_all_leds_with_token(self, values, token, sender_id=None):
        """
        """
        return False

    @dbus.service.method(PI_HAT_IFACE, in_signature='i(ddd)s', out_signature='b', sender_keyword='sender_id')
    def set_led_with_token(self, num, rgb, token, sender_id=None):
        """
        """
        return False

    # --- LED Programming API -----------------------------------------------------------

    @dbus.service.method(PI_HAT_IFACE, in_signature='', out_signature='b', sender_keyword='sender_id')
    def set_leds_off(self, sender_id=None):
        """
        """
        return False

    @dbus.service.method(PI_HAT_IFACE, in_signature='a(ddd)', out_signature='b', sender_keyword='sender_id')
    def set_all_leds(self, values, sender_id=None):
        """
        """
        return False

    @dbus.service.method(PI_HAT_IFACE, in_signature='i(ddd)', out_signature='b', sender_keyword='sender_id')
    def set_led(self, num, rgb, sender_id=None):
        """
        """
        return False

    @dbus.service.method(PI_HAT_IFACE, in_signature='', out_signature='i')
    def get_num_leds(self):
        """
        Get the number of LEDs the LED Speaker has.

        Returns:
            NUM_LEDS - integer number of LEDs
        """
        return self.NUM_LEDS
