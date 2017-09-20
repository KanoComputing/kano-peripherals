# detection.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# A collection of helper functions to interrogate the hardware.


import traceback
from distutils.version import LooseVersion

from kano.logging import logger

from kano_settings.system.display import get_edid_name

from kano_peripherals.pi_hat.driver.service import PiHatService
from kano_peripherals.pi_hat.driver.high_level import get_pihat_interface
from kano_peripherals.ck2_pro_hat.driver.service import CK2ProHatService
from kano_peripherals.ck2_pro_hat.driver.high_level import get_ck2_pro_hat_interface


CKL_V_1_0_0 = LooseVersion('1.0.0')

CKC_V_1_0_0 = LooseVersion('1.0.0')
CKC_V_1_1_0 = LooseVersion('1.1.0')


def is_pi_hat_plugged(with_dbus=True, retry_count=5):
    """
    Check if the Kano PiHat board is plugged in.

    Args:
        with_dbus - bool whether to run the detection through the central dbus
            kano-boards-daemon, or bypass to use the underlyning library
        retry_count - int the number of retries attempted when grabbing a dbus iface

    Returns:
        is_plugged - bool whether the PiHat is plugged in or not.

    NOTE: Running this function with_dbus=False must be done when the daemon is
          certainly not running. Otherwise, bad things might happen.
    """
    is_plugged = False

    try:
        if with_dbus:
            pihat_iface = get_pihat_interface(retry_count=retry_count)
            is_plugged = bool(pihat_iface and pihat_iface.detect())
        else:
            is_plugged = PiHatService.quick_detect()
    except:
        logger.error('Unexpected error occured:\n{}'.format(traceback.format_exc()))

    return is_plugged


def is_power_hat_plugged(with_dbus=True, retry_count=5):
    """
    Check if the Kano PowerHat board is plugged in.

    Args:
        with_dbus - bool whether to run the detection through the central dbus
            kano-boards-daemon, or bypass to use the underlyning library
        retry_count - int the number of retries attempted when grabbing a dbus iface

    Returns:
        is_plugged - bool whether the PowerHat is plugged in or not.

    NOTE: Running this function with_dbus=False must be done when the daemon is
          certainly not running. Otherwise, bad things might happen.
    """
    is_plugged = False

    try:
        if with_dbus:
            ck2prohat_iface = get_ck2_pro_hat_interface(retry_count=retry_count)
            is_plugged = bool(ck2prohat_iface and ck2prohat_iface.detect())
        else:
            is_plugged = CK2ProHatService.quick_detect()
    except:
        logger.error('Unexpected error occured:\n{}'.format(traceback.format_exc()))

    return is_plugged


def is_ck2_lite(with_dbus=True, retry_count=5):
    """
    Check if the hardware is recognised as a Computer Kit (2) Lite.

    At the moment this relies on PiHat board being plugged in.
    Reimplement as the spec changes.

    Args:
        with_dbus - bool as passed to is_pi_hat_plugged function
        retry_count - int as passed to is_pi_hat_plugged function

    Returns:
        is_ck2_lite - bool whether this is a CK2 Lite or not.
    """
    return is_pi_hat_plugged(with_dbus=with_dbus, retry_count=retry_count)


def is_ck2_pro(with_dbus=True, retry_count=5):
    """
    Check if the hardware is recognised as a Computer Kit (2) Pro.

    At the moment this relies on PowerHat board being plugged in.
    Reimplement as the spec changes.

    Args:
        with_dbus - bool as passed to is_power_hat_plugged function
        retry_count - int as passed to is_power_hat_plugged function

    Returns:
        is_ck2_pro - bool whether this is a CK2 Pro or not.
    """
    return is_power_hat_plugged(with_dbus=with_dbus, retry_count=retry_count)


def get_ck2_lite_version():
    """
    Get the version of the Computer Kit Lite.

    The CKL does not currently have any versions so update as required.

    NOTE: This does not do the detection and it assumes it is already the case.
          Use is_ck2_lite() before calling this function.

    Returns:
        LooseVersion object for versions which are detectable, None otherwise.
    """
    return CKL_V_1_0_0


def get_ck2_pro_version():
    """
    Get the version of the Computer Kit Complete.

    NOTE: This does not do the detection and it assumes it is already the case.
          Use is_ck2_pro() before calling this function.

    Returns:
        LooseVersion object for versions which are detectable, None otherwise.
    """
    edid_model = get_edid_name()

    # The v1 was the first batch manufactured and the only hardware
    # characteristic to distinguish it was the model name of the screen
    # which was changed (to MST-HDMI) come first production of CKCs.
    if edid_model == 'MST-HDMI':
        return CKC_V_1_0_0

    # The v1.1 was the second batch manufactured and the only hardware
    # characteristic to distinguish it was the model name of the screen
    # which was changed (to HTC-HDMI) for the second production run of CKCs.
    if edid_model == 'HTC-HDMI':
        return CKC_V_1_1_0

    # Any version above (or other) is marked as 'undefined'.
    return None
