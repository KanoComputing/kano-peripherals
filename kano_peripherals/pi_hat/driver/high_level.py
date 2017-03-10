# high_level.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# TODO: Description


import time
import dbus
import dbus.exceptions

from kano.logging import logger

from kano_peripherals.paths import BUS_NAME, PI_HAT_OBJECT_PATH, PI_HAT_IFACE


# catch signals to allow clean exit
interrupted = False


def setup_signal_handler():
    signal.signal(signal.SIGINT, signal_handler)


def signal_handler(signal, frame):
    global interrupted
    interrupted = True

    pihat_iface = get_pihat_interface()
    if not pihat_iface:
        return

    pihat_iface.unlock()


def get_pihat_interface(retry_count=15):
    dbus_entrypoint = None
    retrying = False

    for r in range(1, retry_count):
        try:
            dbus_entrypoint = dbus.Interface(
                dbus.SystemBus().get_object(BUS_NAME, PI_HAT_OBJECT_PATH),
                PI_HAT_IFACE
            )
        except dbus.exceptions.DBusException:
            retrying = True
            time.sleep(1)
        except Exception as e:
            logger.error('Something unexpected occured in get_pihat_interface - [{}]'
                         .format(e))
            break

    if not dbus_entrypoint and retrying:
        logger.warn('LED Speaker DBus not found. Is kano-boards-daemon running?')

    return dbus_entrypoint
