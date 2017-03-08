# service.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#


import os
import math
import dbus
import dbus.service

from gi.repository import GObject

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

    def __init__(self, bus_name):
        dbus.service.Object.__init__(self, bus_name, PI_HAT_OBJECT_PATH)

    @dbus.service.method(PI_HAT_IFACE, in_signature='', out_signature='i')
    def get_num_leds(self):
        """
        Get the number of LEDs the LED Speaker has.

        Returns:
            NUM_LEDS - integer number of LEDs
        """
        return self.NUM_LEDS
