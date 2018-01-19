# high_level.py
#
# Copyright (C) 2017-2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Helpers for higher level programming of the Pi Hat.


from kano_peripherals.utils import get_service_interface
from kano_peripherals.paths import CK2_PRO_HAT_OBJECT_PATH, SERVICE_API_IFACE


def get_ck2_pro_hat_interface(retry_count=5, retry_time_sec=1):
    """Get a D-Bus interface for the PowerHat board.

    Args:
        retry_count: See :func:`~kano_peripherals.utils.get_service_interface`
        retry_time_sec: See :func:`~kano_peripherals.utils.get_service_interface`

    Returns:
        See :func:`~kano_peripherals.utils.get_service_interface`
    """
    return get_service_interface(
        CK2_PRO_HAT_OBJECT_PATH,
        SERVICE_API_IFACE,
        retry_count=retry_count,
        retry_time_sec=retry_time_sec
    )
