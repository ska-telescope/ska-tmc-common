import pytest

from ska_tmc_common import (
    DishDeviceInfo,
    InputParameter,
    LivelinessProbeType,
    TmcComponentManager,
    TmcLeafNodeComponentManager,
)
from tests.settings import logger


@pytest.fixture
def dev_name():
    # dummy device for testing
    return "dummy/monitored/device"


def test_stop():
    cm = TmcComponentManager(
        _input_parameter=InputParameter(None), logger=logger
    )
    lp = cm.liveliness_probe_object
    assert lp._thread.is_alive()

    cm.stop_liveliness_probe()
    assert lp._stop


@pytest.mark.skip(
    reason="This test fails intermittently, will be fixes as a part of HM-349"
)
def test_stop_ln(dev_name):
    device = DishDeviceInfo(dev_name)
    cm = TmcLeafNodeComponentManager(
        logger=logger, _liveliness_probe=LivelinessProbeType.SINGLE_DEVICE
    )
    cm._device = device
    assert cm._device.dev_name == dev_name
    assert cm.liveliness_probe_object._thread.is_alive()

    cm.stop_liveliness_probe()
    assert cm.liveliness_probe_object._stop


def test_add_device(dev_name):
    cm = TmcComponentManager(
        _input_parameter=InputParameter(None),
        logger=logger,
    )
    lp = cm.liveliness_probe_object
    initial_size = lp._monitoring_devices._qsize()
    lp.add_device(dev_name)

    assert lp._monitoring_devices._qsize() == initial_size + 1
