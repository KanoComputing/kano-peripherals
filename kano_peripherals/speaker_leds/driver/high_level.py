# high_level.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Low level programming of the LED chip. Also includes linerarity adjustment.
# Setup of the chip useds pwm_driver.py, but led programming does not go
# via that file to avoid overhead.


import time
import math
import dbus
import dbus.exceptions
import signal

from kano.logging import logger

from kano_peripherals.paths import BUS_NAME, SPEAKER_LEDS_OBJECT_PATH, SPEAKER_LEDS_IFACE


# catch signals to allow clean exit
interrupted = False


def setup_signal_handler():
    signal.signal(signal.SIGINT, signal_handler)


def signal_handler(signal, frame):
    global interrupted
    interrupted = True

    speakerleds_iface = get_speakerleds_interface()
    if not speakerleds_iface:
        return

    speakerleds_iface.unlock()


def get_speakerleds_interface(retry_count=15):
    dbus_entrypoint = None
    retrying = False

    for r in range(1, retry_count):
        try:
            dbus_entrypoint = dbus.Interface(
                dbus.SystemBus().get_object(BUS_NAME, SPEAKER_LEDS_OBJECT_PATH),
                SPEAKER_LEDS_IFACE
            )
        except dbus.exceptions.DBusException:
            retrying = True
            time.sleep(1)
        except Exception as e:
            logger.error('Something unexpected occured in get_speakerleds_interface - [{}]'
                         .format(e))
            break

    if not dbus_entrypoint and retrying:
        logger.warn('LED Speaker DBus not found. Is kano-boards-daemon running?')

    return dbus_entrypoint
