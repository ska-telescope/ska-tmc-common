import pytest

from ska_tmc_common import (
    BaseLivelinessProbe,
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


def test_stop_ln(dev_name):
    device = DishDeviceInfo(dev_name)
    cm = TmcLeafNodeComponentManager(
        logger=logger, _liveliness_probe=LivelinessProbeType.SINGLE_DEVICE
    )
    cm.start_liveliness_probe(LivelinessProbeType.SINGLE_DEVICE)
    cm._device = device
    assert cm._device.dev_name == dev_name
    assert cm.liveliness_probe_object._thread.is_alive()
    prev_obj = cm.liveliness_probe_object
    cm.start_liveliness_probe(cm._liveliness_probe)
    # does not start again
    assert id(prev_obj) == id(cm.liveliness_probe_object)
    cm.stop_liveliness_probe()
    assert cm.liveliness_probe_object._stop


def test_base_not_implemented_exception():
    base_probe = BaseLivelinessProbe()
    with pytest.raises(NotImplementedError):
        base_probe.run()


def test_add_and_remove_device(dev_name):
    cm = TmcComponentManager(
        _input_parameter=InputParameter(None),
        logger=logger,
    )
    lp = cm.liveliness_probe_object
    initial_size = len(lp._monitoring_devices)
    lp.add_device(dev_name)
    lp.add_device(dev_name)
    lp.add_device(dev_name)

    assert len(lp._monitoring_devices) == initial_size + 1

    lp.remove_devices([dev_name])
    assert len(lp._monitoring_devices) == initial_size
    lp.remove_devices([dev_name])
    assert len(lp._monitoring_devices) == initial_size
