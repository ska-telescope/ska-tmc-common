from ska_tmc_common import (
    DishDeviceInfo,
    InputParameter,
    LivelinessProbeType,
    TmcComponentManager,
    TmcLeafNodeComponentManager,
)
from tests.settings import logger


def test_stop():
    cm = TmcComponentManager(
        _input_parameter=InputParameter(None), logger=logger
    )
    lp = cm.liveliness_probe_object
    assert lp._thread.is_alive()

    cm.stop_liveliness_probe()
    assert lp._stop


def test_stop_ln():
    cm = TmcLeafNodeComponentManager(
        logger=logger, _liveliness_probe=LivelinessProbeType.SINGLE_DEVICE
    )
    device = DishDeviceInfo("dummy/monitored/device")
    cm._device = device

    assert cm.liveliness_probe_object._thread.is_alive()

    cm.stop_liveliness_probe()
    assert cm.liveliness_probe_object._stop


def test_add_device():
    cm = TmcComponentManager(
        _input_parameter=InputParameter(None), logger=logger
    )
    lp = cm.liveliness_probe_object
    initial_size = lp._monitoring_devices._qsize()
    lp.add_device("dummy/monitored/device")

    assert lp._monitoring_devices._qsize() == initial_size + 1
