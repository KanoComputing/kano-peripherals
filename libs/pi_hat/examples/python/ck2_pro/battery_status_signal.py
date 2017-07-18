#!/usr/bin/env python
#
# battery_status_signal.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# Interfacing with the power button through the high-level interface
#


import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

import paths
from kano_peripherals.paths import CK2_PRO_HAT_OBJECT_PATH, SERVICE_API_IFACE, \
    BUS_NAME as CK2_PRO_HAT_BUS_NAME


def battery_changed_cb(level):
    print 'Battery level changed to {}%'.format(level)


if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)

    '''
    Connect to DBus signal:
        Bus: System
        Bus Name: me.kano.boards
        Interface: me.kano.boards.PiHat
        Object Path: /me/kano/boards/PiHat
        Signal: power_button_pressed
    '''
    dbus.SystemBus().add_signal_receiver(
        battery_changed_cb, 'power_level_changed', SERVICE_API_IFACE,
        CK2_PRO_HAT_BUS_NAME, CK2_PRO_HAT_OBJECT_PATH
    )

    GLib.MainLoop().run()
