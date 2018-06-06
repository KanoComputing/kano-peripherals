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
from kano_peripherals.ck2_pro_hat.driver.high_level import \
    get_ck2_pro_hat_interface


CKL, CKC, CKT = xrange(3)


CKL_V_1_0_0 = LooseVersion('1.0.0')

CKC_V_1_0_0 = LooseVersion('1.0.0')
CKC_V_1_1_0 = LooseVersion('1.1.0')

CKT_V_1_0_0 = LooseVersion('1.0.0')


EDID_MAP = {
    # The v1 was the first batch manufactured and the only hardware
    # characteristic to distinguish it was the model name of the screen
    # which was changed (to MST-HDMI) come first production of CKCs.
    'MST-HDMI': (CKC, CKC_V_1_0_0),
    # The v1.1 was the second batch manufactured and the only hardware
    # characteristic to distinguish it was the model name of the screen
    # which was changed (to HTC-HDMI) for the second production run of CKCs.
    'HTC-HDMI': (CKC, CKC_V_1_1_0),
    # FIXME: Insert the correct CKT EDID here when it is available
    'CKT-HDMI': (CKT, CKT_V_1_0_0)
}


def is_pi_hat_plugged(with_dbus=True, retry_count=5):
    """Check if the Kano PiHat board is plugged in.

    NOTE: Running this function with_dbus=False must be done when the daemon is
          certainly not running. Otherwise, bad things might happen.

    Args:
        with_dbus (bool): Whether to run the detection through the central dbus
            kano-boards-daemon, or bypass to use the underlyning library
        retry_count: See
            :func:`~kano_peripherals.pi_hat.driver.high_level.get_pihat_interface`

    Returns:
        bool: Whether the PiHat is plugged in or not
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
    """Check if the Kano PowerHat board is plugged in.

    NOTE: Running this function with_dbus=False must be done when the daemon is
          certainly not running. Otherwise, bad things might happen.

    Args:
        with_dbus (bool): Whether to run the detection through the central dbus
            kano-boards-daemon, or bypass to use the underlying library
        retry_count: See
            :func:`~kano_peripherals.ck2_pro_hat.driver.high_level.get_ck2_pro_hat_interface`

    Returns:
        bool: Whether the PowerHat is plugged in or not
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
    """Check if the hardware is recognised as a Computer Kit (2) Lite.

    At the moment this relies on PiHat board being plugged in.
    Reimplement as the spec changes.

    Args:
        with_dbus: See :func:`is_pi_hat_plugged`
        retry_count: See :func:`is_pi_hat_plugged`

    Returns:
        bool: Whether this is a CK2 Lite or not
    """
    return is_pi_hat_plugged(with_dbus=with_dbus, retry_count=retry_count)


def get_screen_version():
    '''Retrieves the kit type and version from the EDID data

    Returns:
        (int, distutils.version.LooseVersion):
                Tuple of the kit identifier and the version associated
                with that kit. If this fails, (None, None) is returned
    '''
    edid_model = get_edid_name()

    return EDID_MAP.get(edid_model, (None, None))


def is_ck2_pro(with_dbus=True, retry_count=5):
    """Check if the hardware is recognised as a Computer Kit (2) Pro.

    At the moment this relies on PowerHat board being plugged in.

    Given the EOL of the CKC, we have the full list of EDIDs that can be used
    so use these alone to determine the kit's status so completely disregard
    the PowerHat's presence. Due to the historical requirement to check for
    the PowerHat, the arguments `with_dbus` and `retry_count` are no longer
    used but some calls will still be made to them.

    Args:
        with_dbus: See :func:`is_power_hat_plugged` (unused)
        retry_count: See :func:`is_power_hat_plugged` (unused)

    Returns:
        bool: Whether this is a CK2 Pro or not
    """
    kit, dummy_version = get_screen_version()

    return kit == CKC


def is_ckt(with_dbus=True, retry_count=5):
    """Check if the hardware is recognised as a Computer Kit Touch.

    The determination is based on the PowerHat board being plugged in along with
    a matching EDID for the CKT kits.

    This will become the default for any kit which has a PowerHat plugged in
    and the EDID is unknown - essentially the implementation is that a PowerHat
    is connected and it isn't a CKC; this is so that if any EDIDs slip through,
    the kit will still function as intended.

    Reimplement as the spec changes.

    Args:
        with_dbus: See :func:`is_power_hat_plugged`
        retry_count: See :func:`is_power_hat_plugged`

    Returns:
        bool: Whether this is a CKT or not
    """
    hat_connected = is_power_hat_plugged(
        with_dbus=with_dbus, retry_count=retry_count
    )

    if not hat_connected:
        return False

    return not is_ck2_pro(with_dbus, retry_count)


def get_ck2_lite_version():
    """Get the version of the Computer Kit Lite.

    The CKL does not currently have any versions so update as required.

    NOTE: This does not do the detection and it assumes it is already the case.
          Use :func:`~is_ck2_lite()` before calling this function.

    Returns:
        distutils.version.LooseVersion:
            For versions which are detectable, None otherwise
    """
    return CKL_V_1_0_0


def get_ck2_pro_version():
    """Get the version of the Computer Kit Complete.

    NOTE: This does not do the detection and it assumes it is already the case.
          Use :func:`~is_ck2_pro()` before calling this function.

    Returns:
        distutils.version.LooseVersion:
            For versions which are detectable, None otherwise
    """
    dummy_kit, version = get_screen_version()

    return version


def get_ckt_version():
    dummy_kit, version = get_screen_version()

    return version
