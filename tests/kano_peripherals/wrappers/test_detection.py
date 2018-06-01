import pytest

from tests.fixtures.hw_config import HWConfig


def test_is_ck2_lite(hardware_config):
    from kano_peripherals.wrappers.detection import is_ck2_lite

    assert is_ck2_lite() == (hardware_config.kit == HWConfig.CKL)


def test_is_ck2_pro(hardware_config):
    from kano_peripherals.wrappers.detection import is_ck2_pro

    assert is_ck2_pro() == (hardware_config.kit == HWConfig.CKC)


def test_is_ckt(hardware_config):
    from kano_peripherals.wrappers.detection import is_ckt

    assert is_ckt() == (hardware_config.kit == HWConfig.CKT)


def test_get_ck2_lite_version(hardware_config):
    from kano_peripherals.wrappers.detection import get_ck2_lite_version

    if hardware_config.kit != HWConfig.CKL:
        pytest.skip('Function assumes correct kit')

    assert get_ck2_lite_version() == hardware_config.version


def test_get_ck2_pro_version(hardware_config):
    from kano_peripherals.wrappers.detection import get_ck2_pro_version

    if hardware_config.kit != HWConfig.CKC:
        pytest.skip('Function assumes correct kit')

    assert get_ck2_pro_version() == hardware_config.version


def test_get_ckt_version(hardware_config):
    from kano_peripherals.wrappers.detection import get_ckt_version

    if hardware_config.kit != HWConfig.CKT:
        pytest.skip('Function assumes correct kit')

    assert get_ckt_version() == hardware_config.version
