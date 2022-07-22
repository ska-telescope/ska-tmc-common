from ska_tango_base.control_model import HealthState, ObsState
from tango import DevState

from ska_tmc_common.device_info import DeviceInfo, SubArrayDeviceInfo
from ska_tmc_common.input import InputParameter
from ska_tmc_common.test_helpers.helper_tmc_device import DummyComponent
from ska_tmc_common.tmc_component_manager import (
    TmcComponentManager,
    TmcLeafNodeComponentManager,
)
from tests.settings import logger


def test_add_device():
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(
        _input_parameter=InputParameter(None),
        _component=dummy_component,
        logger=logger,
    )
    cm.add_device("dummy/monitored/device")
    cm.add_device("dummy/subarray/device")

    assert len(dummy_component._devices) == 2


def test_get_device():
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(
        _input_parameter=InputParameter(None),
        _component=dummy_component,
        logger=logger,
    )
    cm.add_device("dummy/monitored/device")

    dummy_device_info = cm.get_device("dummy/monitored/device")
    assert dummy_device_info.dev_name == "dummy/monitored/device"


def test_update_device():
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(
        _input_parameter=InputParameter(None),
        _component=dummy_component,
        logger=logger,
    )
    cm.add_device("dummy/monitored/device")
    device_info = cm.get_device("dummy/monitored/device")
    assert device_info.unresponsive is False

    device_info._unresponsive = True
    cm.update_device_info(device_info)
    new_device_info = cm.get_device("dummy/monitored/device")
    assert new_device_info.unresponsive is True


def test_get_device_leafnode():
    dummy_device = DeviceInfo("dummy/monitored/device")
    cm = TmcLeafNodeComponentManager(logger)
    cm._device = dummy_device
    dummy_device_info = cm.get_device()
    assert dummy_device_info.dev_name == "dummy/monitored/device"


def test_update_device_health_state_leafnode():
    dummy_device = DeviceInfo("dummy/monitored/device")
    cm = TmcLeafNodeComponentManager(logger)
    cm._device = dummy_device
    dummy_device_info = cm.get_device()
    assert dummy_device_info.health_state == HealthState.UNKNOWN

    cm.update_device_health_state(HealthState.OK)
    assert dummy_device_info.health_state == HealthState.OK


def test_update_device_state_leafnode():
    dummy_device = DeviceInfo("dummy/monitored/device")
    cm = TmcLeafNodeComponentManager(logger)
    cm._device = dummy_device
    dummy_device_info = cm.get_device()
    assert dummy_device_info.state == DevState.UNKNOWN

    cm.update_device_state(DevState.ON)
    assert dummy_device_info.state == DevState.ON


def test_update_device_obs_state_leafnode():
    dummy_device = SubArrayDeviceInfo("dummy/subarray/device")
    cm = TmcLeafNodeComponentManager(logger)
    cm._device = dummy_device
    dummy_device_info = cm.get_device()
    assert dummy_device_info.obs_state == ObsState.EMPTY

    cm.update_device_obs_state(ObsState.IDLE)
    assert dummy_device_info.obs_state == ObsState.IDLE
