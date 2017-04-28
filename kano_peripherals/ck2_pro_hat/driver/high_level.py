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

from kano_peripherals.paths import BUS_NAME, CK2_PRO_HAT_OBJECT_PATH, \
    CK2_PRO_HAT_IFACE


def get_ck2_pro_hat_interface(retry_count=5):
    iface = None
    successful = False

    for retry in range(1, retry_count):
        try:
            iface = dbus.Interface(
                dbus.SystemBus().get_object(BUS_NAME, CK2_PRO_HAT_OBJECT_PATH),
                CK2_PRO_HAT_IFACE
            )
            iface.hello_world()
        except dbus.exceptions.DBusException, dbus.exceptions.UnknownMethodException:
            time.sleep(1)
            continue
        except Exception as e:
            logger.error(
                'get_ck2_pro_hat_interface: Unexpected error occured: {}\n'
                .format(e)
            )
            break
        successful = True

    if not iface or not successful:
        logger.warn('CK2ProHat DBus not found. Is kano-boards-daemon running?')
        return None

    return iface
