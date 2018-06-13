import imp
import pytest

from kano_peripherals.wrappers.detection import CKL_V_1_0_0, CKC_V_1_0_0, \
    CKC_V_1_1_0, CKT_V_1_0_0


class HWConfig(object):
    CKL = 'CKL'
    CKC = 'CKC'
    CKT = 'CKT'

    def __init__(self, kit, version, edid):
        self.kit = kit
        self.version = version
        self.edid = edid


HW_CONFIG = [
    # Kit type, kit version, EDID
    HWConfig(HWConfig.CKL, CKL_V_1_0_0, 'ANY'),
    HWConfig(HWConfig.CKC, CKC_V_1_0_0, 'MST-HDMI'),
    HWConfig(HWConfig.CKC, CKC_V_1_1_0, 'HTC-HDMI'),
    HWConfig(HWConfig.CKT, CKT_V_1_0_0, 'HCK-HDMI'),
]


@pytest.fixture(scope='function', params=HW_CONFIG)
def hardware_config(request, monkeypatch, fs):
    '''
    Simulates the hardware configuration by mocking the
    `kano_settings.system.display.get_edid_name()`
    function and overriding the `is_power_hat_plugged()` and
    `is_pi_hat_plugged()` functions from `kano_peripherals.wrappers.detection`.

    Returns:
        HWConfig: The hardware configuration simulated
    '''

    import kano_settings.system.display
    import kano_peripherals.wrappers.detection

    hw = request.param

    monkeypatch.setattr(
        kano_settings.system.display, 'get_edid_name', lambda: hw.edid
    )

    # Reimport to allow the get_edid_name patch to permeate for each parameter
    imp.reload(kano_peripherals.wrappers.detection)
    monkeypatch.setattr(
        kano_peripherals.wrappers.detection,
        'is_pi_hat_plugged',
        lambda with_dbus, retry_count: hw.kit == HWConfig.CKL
    )
    monkeypatch.setattr(
        kano_peripherals.wrappers.detection,
        'is_power_hat_plugged',
        lambda with_dbus, retry_count: \
            hw.kit == HWConfig.CKC or hw.kit == HWConfig.CKT
    )

    return hw


