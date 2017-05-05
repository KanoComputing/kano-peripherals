# detection.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# A collection of helper functions to interrogate the hardware.


import traceback

from kano.logging import logger

from kano_peripherals.pi_hat.driver.high_level import get_pihat_interface
from kano_peripherals.ck2_pro_hat.driver.high_level import get_ck2_pro_hat_interface


def is_pi_hat_plugged():
    """
    Check if the Kano PiHat board is plugged in.

    Returns:
        is_plugged - bool whether the PiHat is plugged in or not.
    """
    is_plugged = False

    try:
        pihat_iface = get_pihat_interface(retry_count=5)
        is_plugged = (pihat_iface and pihat_iface.detect())
    except:
        logger.error('Unexpected error occured:\n{}'.format(traceback.format_exc()))

    return is_plugged


def is_power_hat_plugged():
    """
    Check if the Kano PowerHat board is plugged in.

    Returns:
        is_plugged - bool whether the PowerHat is plugged in or not.
    """
    is_plugged = False

    try:
        ck2prohat_iface = get_ck2_pro_hat_interface(retry_count=5)
        is_plugged = (ck2prohat_iface and ck2prohat_iface.detect())
    except:
        logger.error('Unexpected error occured:\n{}'.format(traceback.format_exc()))

    return is_plugged


def is_ck2_lite():
    """
    Check if the hardware is recognised as a Computer Kit (2) Lite.

    At the moment this relies on PiHat board being plugged in.
    Reimplement as the spec changes.

    Returns:
        is_ck2_lite - bool whether this is a CK2 Lite or not.
    """
    return is_pi_hat_plugged()


def is_ck2_pro():
    """
    Check if the hardware is recognised as a Computer Kit (2) Pro.

    At the moment this relies on PowerHat board being plugged in.
    Reimplement as the spec changes.

    Returns:
        is_ck2_pro - bool whether this is a CK2 Pro or not.
    """
    return is_power_hat_plugged()
