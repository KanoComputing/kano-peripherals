# high_level.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Helpers for higher level programming of the Pi Hat.


import time
import dbus
import dbus.exceptions

from kano.logging import logger

from kano_peripherals.paths import BUS_NAME, PI_HAT_OBJECT_PATH, PI_HAT_IFACE


def get_pihat_interface(retry_count=5):
    iface = None

    for retry in range(1, retry_count):
        try:
            iface = dbus.Interface(
                dbus.SystemBus().get_object(BUS_NAME, PI_HAT_OBJECT_PATH),
                PI_HAT_IFACE
            )
        except dbus.exceptions.DBusException:
            time.sleep(1)
        except Exception as e:
            logger.error('get_pihat_interface: Unexpected error occured:\n'.format(e))
            break

    if not iface:
        logger.warn('PiHat DBus not found. Is kano-boards-daemon running?')

    return iface
