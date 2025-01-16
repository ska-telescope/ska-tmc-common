import unittest
from unittest.mock import MagicMock, Mock

from ska_control_model import AdminMode
from tango import EventData

from ska_tmc_common.v1.event_receiver import EventReceiver


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
