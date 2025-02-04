import time

import pytest

from ska_tmc_common import DishDeviceInfo, InputParameter, LivelinessProbeType
from ska_tmc_common.v1.liveliness_probe import BaseLivelinessProbe
from ska_tmc_common.v1.liveliness_probe import (
    BaseLivelinessProbe as baselivelinessprobe,
)
from ska_tmc_common.v1.tmc_component_manager import TmcComponentManager
from ska_tmc_common.v1.tmc_component_manager import (
    TmcComponentManager as TmcCM,
)
from ska_tmc_common.v1.tmc_component_manager import TmcLeafNodeComponentManager
from ska_tmc_common.v1.tmc_component_manager import (
    TmcLeafNodeComponentManager as TmcLNCM,
)
from tests.settings import logger


@pytest.fixture
def dev_name():
    # dummy device for testing
    return "dummy/monitored/device"


@pytest.mark.parametrize("component_manager", [TmcComponentManager, TmcCM])
def test_stop(component_manager):
    cm = component_manager(
        _input_parameter=InputParameter(None), logger=logger
    )
    lp = cm.liveliness_probe_object
    assert lp._thread.is_alive()

    cm.stop_liveliness_probe()
    assert lp._stop


@pytest.mark.skip(reason="Unstable test case")
@pytest.mark.parametrize(
    "component_manager", [TmcLeafNodeComponentManager, TmcLNCM]
)
def test_stop_ln(dev_name, component_manager):
    device = DishDeviceInfo(dev_name)
    cm = component_manager(
        logger=logger, _liveliness_probe=LivelinessProbeType.SINGLE_DEVICE
    )
    cm.start_liveliness_probe(LivelinessProbeType.SINGLE_DEVICE)
    cm._device = device
    assert cm._device.dev_name == dev_name
    prev_obj_id = id(cm.liveliness_probe_object)
    # It was observed that some times this test case fails if
    # liveliness probe takes little extra time to start ,
    # hence this sleep is added.
    time.sleep(0.2)
    assert cm.liveliness_probe_object._thread.is_alive()
    cm.start_liveliness_probe(LivelinessProbeType.SINGLE_DEVICE)
    # does not start again
    assert prev_obj_id == id(cm.liveliness_probe_object)
    cm.stop_liveliness_probe()
    assert cm.liveliness_probe_object._stop


@pytest.mark.parametrize(
    "component_manager, liveliness_probe",
    [
        (TmcLeafNodeComponentManager, BaseLivelinessProbe),
        (TmcLNCM, baselivelinessprobe),
    ],
)
def test_base_not_implemented_exception(component_manager, liveliness_probe):
    cm = component_manager(
        logger=logger, _liveliness_probe=LivelinessProbeType.SINGLE_DEVICE
    )
    base_probe = liveliness_probe(cm, logger)
    with pytest.raises(NotImplementedError):
        base_probe.run()


@pytest.mark.parametrize("component_manager", [TmcComponentManager, TmcCM])
def test_add_and_remove_device(dev_name, component_manager):
    cm = component_manager(
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
