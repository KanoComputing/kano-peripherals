# high_level.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Helpers for higher level programming of the Pi Hat.


from kano_peripherals.utils import get_service_interface
from kano_peripherals.paths import PI_HAT_OBJECT_PATH, PI_HAT_IFACE


def get_pihat_interface(retry_count=5, retry_time_sec=1):
    return get_service_interface(
        PI_HAT_OBJECT_PATH,
        PI_HAT_IFACE,
        retry_count=retry_count,
        retry_time_sec=retry_time_sec
    )
