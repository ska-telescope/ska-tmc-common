"""A module to test the Event Receiver class"""

import time
from unittest.mock import MagicMock, Mock

import pytest
import tango
from ska_control_model import AdminMode, ObsState
from tango import EventData

from ska_tmc_common import DevFactory
from ska_tmc_common.v1.event_receiver import EventReceiver
from tests.settings import (
    SUBARRAY_DEVICE,
    DummyComponentManager,
    create_cm,
    logger,
)

TIMEOUT = 10


def test_event_receiver():
    """Test the initialization, startup and termination of event receiver
    class.
    """
    cm = create_cm()
    event_receiver = EventReceiver(cm, logger)
    event_receiver.start()

    assert event_receiver._thread.is_alive()

    event_receiver.stop()
    start_time = time.time()
    while event_receiver._thread.is_alive():
        if time.time() - start_time > TIMEOUT:
            pytest.fail(
                reason="Timeout occured while waiting for Event Receiver "
                + "thread to stop."
            )


def test_event_subscription_default(tango_context):
    """Tests the event subscription on a tango device."""
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)

    cm = DummyComponentManager(logger)
    cm.add_device(SUBARRAY_DEVICE)
    event_receiver = EventReceiver(cm, logger)
    event_receiver.start()

    subarray_device.SetDirectObsState(ObsState.READY)
    start_time = time.time()
    while cm.get_device().obs_state != ObsState.READY:
        if time.time() - start_time > TIMEOUT:
            event_receiver.stop()
            pytest.fail(
                reason="Timeout occured while waiting for obsState event to be"
                + " received."
            )
    event_receiver.stop()


def test_event_subscription_additional_attributes(tango_context):
    """Tests the event subscription for additional attributes on a tango
    device."""
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)

    def event_handler(event: tango.EventData) -> None:
        """An event handler method for testing."""
        if event.err:
            error = event.errors[0]
            logger.error("%s: %s", error.reason, error.desc)
            cm.update_event_failure(event.device.dev_name())
            return
        new_value = event.attr_value.value
        event_handler.command_in_progress = new_value

    event_handler.command_in_progress = ""

    cm = DummyComponentManager(logger)
    cm.add_device(SUBARRAY_DEVICE)
    attribute_dict = {
        "commandInProgress": event_handler,
    }
    event_receiver = EventReceiver(cm, logger, attribute_dict)
    event_receiver.start()

    subarray_device.SetDirectCommandInProgress("AssignResources")
    start_time = time.time()
    while event_handler.command_in_progress != "AssignResources":
        if time.time() - start_time > TIMEOUT:
            event_receiver.stop()
            pytest.fail(
                reason="Timeout occured while waiting for commandInProgress "
                + "event to be received."
            )
    event_receiver.stop()


def test_handle_admin_mode_event_success():
    # Mock the component manager and logger
    component_manager = Mock()
    component_manager.is_admin_mode_enabled = True
    logger = Mock()

    # Initialize the EventReceiver with mocks
    event_receiver = EventReceiver(
        component_manager=component_manager,
        logger=logger,
    )

    # Create a mock Tango EventData object
    mock_event = Mock(spec=EventData)
    mock_event.err = False
    mock_event.attr_value.value = AdminMode.ONLINE
    mock_event.device.dev_name.return_value = "test/device/1"

    # Call the method under test
    event_receiver.handle_admin_mode_event(mock_event)

    # Assert the logger info method was called
    logger.info.assert_any_call(
        "Received an adminMode event with : %s for device: %s",
        AdminMode.ONLINE,
        "test/device/1",
    )
    logger.debug.assert_called_once_with(
        "Admin Mode updated to :%s", AdminMode.ONLINE.name
    )

    # Assert the component manager method was called
    component_manager.update_device_admin_mode.assert_called_once_with(
        "test/device/1", AdminMode.ONLINE
    )


def test_handle_admin_mode_event_with_error():
    # Mock the component manager and logger
    component_manager = Mock()
    logger = Mock()

    # Initialize the EventReceiver with mocks
    event_receiver = EventReceiver(
        component_manager=component_manager,
        logger=logger,
    )

    # Create a mock Tango EventData object with error
    mock_event = Mock(spec=EventData)
    mock_event.err = True
    mock_event.errors = [
        MagicMock(reason="ErrorReason", desc="ErrorDescription")
    ]
    mock_event.device.dev_name.return_value = "test/device/2"

    # Call the method under test
    event_receiver.handle_admin_mode_event(mock_event)

    # Assert the logger error method was called
    logger.error.assert_called_once_with("ErrorReason,ErrorDescription")

    # Assert the component manager's update_event_failure was called
    component_manager.update_event_failure.assert_called_once_with(
        "test/device/2"
    )


def test_handle_admin_mode_event_when_disabled():
    # Mock the component manager and logger
    component_manager = Mock()
    component_manager.is_admin_mode_enabled = False
    logger = Mock()

    # Initialize the EventReceiver with mocks
    event_receiver = EventReceiver(
        component_manager=component_manager,
        logger=logger,
    )

    # Create a mock Tango EventData object
    mock_event = Mock(spec=EventData)

    # Call the method under test
    event_receiver.handle_admin_mode_event(mock_event)

    # Assert no logger or component manager methods were called
    logger.error.assert_not_called()
    logger.info.assert_not_called()
    component_manager.update_device_admin_mode.assert_not_called()
    component_manager.update_event_failure.assert_not_called()
