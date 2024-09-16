import time

import pytest
import tango
from ska_tango_base.control_model import HealthState, ObsState
from tango import DevState

from ska_tmc_common import (
    DeviceInfo,
    DummyComponent,
    InputParameter,
    SubArrayDeviceInfo,
    TmcComponentManager,
    TmcLeafNodeComponentManager,
)
from ska_tmc_common.enum import LivelinessProbeType
from tests.settings import (
    DUMMY_MONITORED_DEVICE,
    DUMMY_SUBARRAY_DEVICE,
    logger,
)


def test_add_device():
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(
        _input_parameter=InputParameter(None),
        _component=dummy_component,
        logger=logger,
    )
    cm.add_device(DUMMY_MONITORED_DEVICE)
    cm.add_device(DUMMY_SUBARRAY_DEVICE)

    assert len(dummy_component._devices) == 2


def test_get_device():
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(
        _input_parameter=InputParameter(None),
        _component=dummy_component,
        logger=logger,
    )
    cm.add_device(DUMMY_MONITORED_DEVICE)

    dummy_device_info = cm.get_device(DUMMY_MONITORED_DEVICE)
    assert dummy_device_info.dev_name == DUMMY_MONITORED_DEVICE


def test_update_device():
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(
        _input_parameter=InputParameter(None),
        _component=dummy_component,
        logger=logger,
    )
    cm.add_device(DUMMY_MONITORED_DEVICE)
    device_info = cm.get_device(DUMMY_MONITORED_DEVICE)
    assert device_info.unresponsive is False

    device_info._unresponsive = True
    cm.update_device_info(device_info)
    new_device_info = cm.get_device(DUMMY_MONITORED_DEVICE)
    assert new_device_info.unresponsive is True


def test_get_device_leafnode():
    dummy_device = DeviceInfo(DUMMY_MONITORED_DEVICE)
    cm = TmcLeafNodeComponentManager(logger)
    cm._device = dummy_device
    dummy_device_info = cm.get_device()
    assert dummy_device_info.dev_name == DUMMY_MONITORED_DEVICE


def test_update_device_health_state_leafnode():
    dummy_device = DeviceInfo(DUMMY_MONITORED_DEVICE)
    cm = TmcLeafNodeComponentManager(logger)
    cm._device = dummy_device
    dummy_device_info = cm.get_device()
    assert dummy_device_info.health_state == HealthState.UNKNOWN

    cm.update_device_health_state(DUMMY_MONITORED_DEVICE, HealthState.OK)
    assert dummy_device_info.health_state == HealthState.OK


def test_update_device_state_leafnode():
    dummy_device = DeviceInfo(DUMMY_MONITORED_DEVICE)
    cm = TmcLeafNodeComponentManager(logger)
    cm._device = dummy_device
    dummy_device_info = cm.get_device()
    assert dummy_device_info.state == DevState.UNKNOWN

    cm.update_device_state(DUMMY_MONITORED_DEVICE, DevState.ON)
    assert dummy_device_info.state == DevState.ON


def test_update_device_obs_state_leafnode():
    dummy_device = SubArrayDeviceInfo(DUMMY_SUBARRAY_DEVICE)
    cm = TmcLeafNodeComponentManager(logger)
    cm._device = dummy_device
    dummy_device_info = cm.get_device()
    assert dummy_device_info.obs_state == ObsState.EMPTY

    cm.update_device_obs_state(DUMMY_SUBARRAY_DEVICE, ObsState.IDLE)
    assert dummy_device_info.obs_state == ObsState.IDLE


def test_start_liveliness_probe_single_device(component_manager):
    component_manager.start_liveliness_probe(LivelinessProbeType.SINGLE_DEVICE)
    assert component_manager.liveliness_probe_object is not None


def test_update_exception_for_unresponsiveness(component_manager):
    # Test if update_exception_for_unresponsiveness sets the
    # device's exception and does not raise an exception
    exception = "test exception"
    dev_info = component_manager.get_device()
    component_manager.update_exception_for_unresponsiveness(
        dev_info, exception
    )
    assert component_manager.get_device().exception == exception


def test_update_device_info(component_manager):
    # Test if update_device_info sets the
    # device info and does not raise an exception
    device_info = DeviceInfo(DUMMY_MONITORED_DEVICE)
    component_manager.update_device_info(device_info)
    assert component_manager.get_device() == device_info


def test_update_responsiveness_info(component_manager):
    # Test if update_ping_info sets the
    # device's ping and does not raise an exception

    dev_name = DUMMY_MONITORED_DEVICE
    component_manager.update_responsiveness_info(dev_name)
    assert not component_manager.get_device().unresponsive


def test_update_device_health_state(component_manager):
    # Test if update_device_health_state updates the
    # device's health state and does not raise an exception
    health_state = HealthState.OK
    component_manager.update_device_health_state(
        DUMMY_MONITORED_DEVICE, health_state
    )
    assert component_manager.get_device().health_state == health_state
    assert component_manager.get_device().last_event_arrived == pytest.approx(
        time.time(), abs=1e-3
    )
    assert not component_manager.get_device().unresponsive


def test_update_device_state(component_manager):
    # Test if update_device_state updates
    # the device's state and does not raise an exception
    state = tango.DevState.ON
    component_manager.update_device_state(DUMMY_MONITORED_DEVICE, state)
    assert component_manager.get_device().state == state
    assert component_manager.get_device().last_event_arrived == pytest.approx(
        time.time(), abs=1e-3
    )
    assert not component_manager.get_device().unresponsive


def test_update_device_obs_state(component_manager):
    # Test if update_device_obs_state updates
    # the device's obs state and does not raise an exception
    obs_state = ObsState.READY
    component_manager.update_device_obs_state(
        DUMMY_MONITORED_DEVICE, obs_state
    )
    assert component_manager.get_device().obs_state == obs_state
    assert component_manager.get_device().last_event_arrived == pytest.approx(
        time.time(), abs=1e-3
    )
    assert not component_manager.get_device().unresponsive


def test_command_id_property(component_manager):
    # Test if command id property can be accessed and set correctly
    assert component_manager.command_id == ""
    new_id = f"{time.time()}-TempID"
    component_manager.command_id = new_id
    assert component_manager.command_id == new_id
