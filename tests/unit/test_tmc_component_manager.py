import time
from unittest.mock import MagicMock, Mock

import pytest
import tango
from ska_tango_base.control_model import AdminMode, HealthState
from tango import DevState, EventData

from ska_tmc_common import DeviceInfo, DummyComponent, InputParameter
from ska_tmc_common.enum import LivelinessProbeType
from ska_tmc_common.v1.tmc_component_manager import BaseTmcComponentManager
from ska_tmc_common.v1.tmc_component_manager import TmcComponentManager
from ska_tmc_common.v1.tmc_component_manager import (
    TmcComponentManager as TmcCM,
)
from ska_tmc_common.v1.tmc_component_manager import TmcLeafNodeComponentManager
from ska_tmc_common.v1.tmc_component_manager import (
    TmcLeafNodeComponentManager as TmcLNCM,
)
from tests.settings import (
    DUMMY_MONITORED_DEVICE,
    DUMMY_SUBARRAY_DEVICE,
    SUBARRAY_DEVICE,
    DummyComponentManager,
    logger,
)


@pytest.mark.parametrize("component_manager", [TmcComponentManager, TmcCM])
def test_add_device(component_manager):
    dummy_component = DummyComponent(logger)
    cm = component_manager(
        _input_parameter=InputParameter(None),
        _component=dummy_component,
        logger=logger,
    )
    cm.add_device(DUMMY_MONITORED_DEVICE)
    cm.add_device(DUMMY_SUBARRAY_DEVICE)

    assert len(dummy_component._devices) == 2


@pytest.mark.parametrize("component_manager", [TmcComponentManager, TmcCM])
def test_get_device(component_manager):
    dummy_component = DummyComponent(logger)
    cm = component_manager(
        _input_parameter=InputParameter(None),
        _component=dummy_component,
        logger=logger,
    )
    cm.add_device(DUMMY_MONITORED_DEVICE)

    dummy_device_info = cm.get_device(DUMMY_MONITORED_DEVICE)
    assert dummy_device_info.dev_name == DUMMY_MONITORED_DEVICE


@pytest.mark.parametrize("component_manager", [TmcComponentManager, TmcCM])
def test_update_device(component_manager):
    dummy_component = DummyComponent(logger)
    cm = component_manager(
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


@pytest.mark.parametrize(
    "component_manager", [TmcLeafNodeComponentManager, TmcLNCM]
)
def test_get_device_leafnode(component_manager):
    dummy_device = DeviceInfo(DUMMY_MONITORED_DEVICE)
    cm = component_manager(logger)
    cm._device = dummy_device
    dummy_device_info = cm.get_device()
    assert dummy_device_info.dev_name == DUMMY_MONITORED_DEVICE


@pytest.mark.parametrize(
    "component_manager", [TmcLeafNodeComponentManager, TmcLNCM]
)
def test_update_device_health_state_leafnode(component_manager):
    dummy_device = DeviceInfo(DUMMY_MONITORED_DEVICE)
    cm = component_manager(logger)
    cm._device = dummy_device
    dummy_device_info = cm.get_device()
    assert dummy_device_info.health_state == HealthState.UNKNOWN

    cm.update_device_health_state(HealthState.OK)
    assert dummy_device_info.health_state == HealthState.OK


@pytest.mark.parametrize(
    "component_manager", [TmcLeafNodeComponentManager, TmcLNCM]
)
def test_update_device_state_leafnode(component_manager):
    dummy_device = DeviceInfo(DUMMY_MONITORED_DEVICE)
    cm = component_manager(logger)
    cm._device = dummy_device
    dummy_device_info = cm.get_device()
    assert dummy_device_info.state == DevState.UNKNOWN

    cm.update_device_state(DevState.ON)
    assert dummy_device_info.state == DevState.ON


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
    dummy_component = DummyComponent(logger)
    component_manager = TmcCM(
        _input_parameter=InputParameter(None),
        _component=dummy_component,
        logger=logger,
    )
    component_manager.add_device(DUMMY_MONITORED_DEVICE)

    health_state = HealthState.OK
    component_manager.update_device_health_state(
        DUMMY_MONITORED_DEVICE, health_state
    )
    assert (
        component_manager.get_device(DUMMY_MONITORED_DEVICE).health_state
        == health_state
    )
    assert component_manager.get_device(
        DUMMY_MONITORED_DEVICE
    ).last_event_arrived == pytest.approx(time.time(), abs=1e-3)
    assert not component_manager.get_device(
        DUMMY_MONITORED_DEVICE
    ).unresponsive


def test_update_device_state(component_manager):
    # Test if update_device_state updates
    # the device's state and does not raise an exception
    state = tango.DevState.ON
    dummy_component = DummyComponent(logger)
    component_manager = TmcCM(
        _input_parameter=InputParameter(None),
        _component=dummy_component,
        logger=logger,
    )
    component_manager.add_device(DUMMY_MONITORED_DEVICE)
    component_manager.update_device_state(DUMMY_MONITORED_DEVICE, state)
    assert component_manager.get_device(DUMMY_MONITORED_DEVICE).state == state
    assert component_manager.get_device(
        DUMMY_MONITORED_DEVICE
    ).last_event_arrived == pytest.approx(time.time(), abs=1e-3)
    assert not component_manager.get_device(
        DUMMY_MONITORED_DEVICE
    ).unresponsive


@pytest.mark.parametrize(
    "event_queue", ["state", "obsState", "healthState", "adminMode"]
)
def test_handle_event_with_error(event_queue):
    # Initialize mocks
    logger = Mock()
    component_manager = DummyComponentManager(logger)
    component_manager.add_device(SUBARRAY_DEVICE)

    # Create a mock Tango EventData object with error
    mock_event = Mock(spec=EventData)
    mock_event.err = True
    mock_event.errors = [
        MagicMock(reason="ErrorReason", desc="ErrorDescription")
    ]
    mock_event.device.dev_name.return_value = "test/device/1"

    component_manager.start_event_processing_threads()
    component_manager.event_queues[event_queue].put(mock_event)

    # Sleep is needed since sometimes test will fail if logger is
    # not yet called
    time.sleep(0.1)

    logger.error.assert_called_once_with(
        "Error occurred on %s for device: %s - %s, %s",
        f"{event_queue}_Callback",
        mock_event.device.dev_name(),
        "ErrorReason",
        "ErrorDescription",
    )


def test_update_device_admin_mode():
    dummy_device = DeviceInfo("dummy/monitored/device")
    component_manager = BaseTmcComponentManager(logger)
    component_manager._device = dummy_device
    admin_mode = AdminMode.ONLINE
    component_manager.update_device_admin_mode(admin_mode)
    assert component_manager.get_device().adminMode == admin_mode
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


def test_admin_mode_property():
    component_manager = BaseTmcComponentManager(logger)
    assert component_manager.is_admin_mode_enabled is True
    component_manager.is_admin_mode_enabled = False
    assert component_manager.is_admin_mode_enabled is False


def test_admin_mode_property_invalid():
    component_manager = BaseTmcComponentManager(logger)
    assert component_manager.is_admin_mode_enabled is True
    with pytest.raises(
        ValueError, match="is_admin_mode_enabled must be a boolean value."
    ):
        component_manager.is_admin_mode_enabled = "False"
