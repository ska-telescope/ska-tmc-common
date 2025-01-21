"""A module to test the Event Receiver class"""

import time
from unittest.mock import MagicMock, Mock

import pytest
import tango
from ska_control_model import ObsState
from tango import EventData

from ska_tmc_common import DevFactory
from ska_tmc_common.event_receiver import EventReceiver
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


def test_handle_obsstate_event_with_error():
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
    event_receiver.handle_obs_state_event(mock_event)

    # Assert the logger error method was called
    logger.error.assert_called_once_with(
        "%s\n %s", "ErrorReason", "ErrorDescription"
    )

    # Assert the component manager's update_event_failure was called
    component_manager.update_event_failure.assert_called_once_with(
        "test/device/2"
    )


def test_handle_healthstate_event_with_error():
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
    event_receiver.handle_health_state_event(mock_event)

    # Assert the logger error method was called
    logger.error.assert_called_once_with(
        "Received error from device %s: %s %s",
        "test/device/2",
        "ErrorReason",
        "ErrorDescription",
    )

    # Assert the component manager's update_event_failure was called
    component_manager.update_event_failure.assert_called_once_with(
        "test/device/2"
    )


def test_handle_state_event_with_error():
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
    event_receiver.handle_state_event(mock_event)

    # Assert the logger error method was called
    logger.error.assert_called_once_with(
        "Reason :%s  Description %s", "ErrorReason", "ErrorDescription"
    )

    # Assert the component manager's update_event_failure was called
    component_manager.update_event_failure.assert_called_once_with(
        "test/device/2"
    )
