# high_level.py
#
# Copyright (C) 2015 - 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Helpers for higher level programming of the LED Speaker.


from kano_peripherals.utils import get_service_interface
from kano_peripherals.paths import SPEAKER_LEDS_OBJECT_PATH, SERVICE_API_IFACE


def get_speakerleds_interface(retry_count=5, retry_time_sec=1):
    return get_service_interface(
        SPEAKER_LEDS_OBJECT_PATH,
        SERVICE_API_IFACE,
        retry_count=retry_count,
        retry_time_sec=retry_time_sec
    )
