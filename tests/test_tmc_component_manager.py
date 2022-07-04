import logging

import pytest
from ska_tango_base.control_model import HealthState, ObsState
from tango import DevState

from ska_tmc_common.device_info import DeviceInfo, SubArrayDeviceInfo
from ska_tmc_common.op_state_model import TMCOpStateModel
from ska_tmc_common.test_helpers.helper_tmc_device import DummyComponent
from ska_tmc_common.tmc_component_manager import (
    TmcComponentManager,
    TmcLeafNodeComponentManager,
)

logger = logging.getLogger(__name__)


def test_add_device():
    op_state_model = TMCOpStateModel(logger)
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(op_state_model, dummy_component, logger)
    cm.add_device("dummy/monitored/device")
    cm.add_device("dummy/subarray/device")

    assert len(dummy_component._devices) == 2


def test_get_device():
    op_state_model = TMCOpStateModel(logger)
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(op_state_model, dummy_component, logger)
    cm.add_device("dummy/monitored/device")

    dummy_device_info = cm.get_device("dummy/monitored/device")
    assert dummy_device_info.dev_name == "dummy/monitored/device"


def test_update_device():
    op_state_model = TMCOpStateModel(logger)
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(op_state_model, dummy_component, logger)
    cm.add_device("dummy/monitored/device")
    device_info = cm.get_device("dummy/monitored/device")
    assert device_info.unresponsive is False

    device_info._unresponsive = True
    cm.update_device_info(device_info)
    new_device_info = cm.get_device("dummy/monitored/device")
    assert new_device_info.unresponsive is True


def test_telescope_on():
    op_state_model = TMCOpStateModel(logger)
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(op_state_model, dummy_component, logger)
    # raise NotImplementedError
    with pytest.raises(NotImplementedError):
        cm.telescope_on()


def test_telescope_off():
    op_state_model = TMCOpStateModel(logger)
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(op_state_model, dummy_component, logger)
    # raise NotImplementedError
    with pytest.raises(NotImplementedError):
        cm.telescope_off()


def test_telescope_standby():
    op_state_model = TMCOpStateModel(logger)
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(op_state_model, dummy_component, logger)
    # raise NotImplementedError
    with pytest.raises(NotImplementedError):
        cm.telescope_standby()


def test_assign_resources():
    op_state_model = TMCOpStateModel(logger)
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(op_state_model, dummy_component, logger)
    # raise NotImplementedError
    with pytest.raises(NotImplementedError):
        cm.assign_resources()


def test_release_resources():
    op_state_model = TMCOpStateModel(logger)
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(op_state_model, dummy_component, logger)
    # raise NotImplementedError
    with pytest.raises(NotImplementedError):
        cm.release_resources()


def test_check_if_command_is_allowed():
    op_state_model = TMCOpStateModel(logger)
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(op_state_model, dummy_component, logger)
    # raise NotImplementedError
    with pytest.raises(NotImplementedError):
        cm.check_if_command_is_allowed()


def test_get_device_leafnode():
    op_state_model = TMCOpStateModel(logger)
    dummy_device = DeviceInfo("dummy/monitored/device")
    cm = TmcLeafNodeComponentManager(op_state_model, logger)
    cm._device = dummy_device
    dummy_device_info = cm.get_device()
    assert dummy_device_info.dev_name == "dummy/monitored/device"


def test_update_device_health_state_leafnode():
    op_state_model = TMCOpStateModel(logger)
    dummy_device = DeviceInfo("dummy/monitored/device")
    cm = TmcLeafNodeComponentManager(op_state_model, logger)
    cm._device = dummy_device
    dummy_device_info = cm.get_device()
    assert dummy_device_info.health_state == HealthState.UNKNOWN

    cm.update_device_health_state(HealthState.OK)
    assert dummy_device_info.health_state == HealthState.OK


def test_update_device_state_leafnode():
    op_state_model = TMCOpStateModel(logger)
    dummy_device = DeviceInfo("dummy/monitored/device")
    cm = TmcLeafNodeComponentManager(op_state_model, logger)
    cm._device = dummy_device
    dummy_device_info = cm.get_device()
    assert dummy_device_info.state == DevState.UNKNOWN

    cm.update_device_state(DevState.ON)
    assert dummy_device_info.state == DevState.ON


def test_update_device_obs_state_leafnode():
    op_state_model = TMCOpStateModel(logger)
    dummy_device = SubArrayDeviceInfo("dummy/subarray/device")
    cm = TmcLeafNodeComponentManager(op_state_model, logger)
    cm._device = dummy_device
    dummy_device_info = cm.get_device()
    assert dummy_device_info.obs_state == ObsState.EMPTY

    cm.update_device_obs_state(ObsState.IDLE)
    assert dummy_device_info.obs_state == ObsState.IDLE
