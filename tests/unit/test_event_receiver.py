"""A module to test the Event Receiver class"""

import time
from unittest.mock import Mock

import pytest
import tango
from ska_control_model import ObsState
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


@pytest.mark.parametrize(
    "event_method, event_queue_key",
    [
        ("handle_state_event", "state"),
        ("handle_health_state_event", "healthState"),
        ("handle_obs_state_event", "obsState"),
    ],
)
def test_event_placed_in_queue(event_method, event_queue_key):
    # Mock the event queue and component manager
    mock_event_queue = Mock()
    component_manager = Mock()
    component_manager.event_queues = {event_queue_key: mock_event_queue}
    logger = Mock()

    # Initialize the EventReceiver with mocks
    event_receiver = EventReceiver(
        component_manager=component_manager,
        logger=logger,
    )

    # Create a mock Tango EventData object
    mock_event = Mock(spec=EventData)

    # Dynamically call the method under test
    method_to_call = getattr(event_receiver, event_method)
    method_to_call(mock_event)

    # Assert that the event was put into the correct queue
    # mock_event_queue.put.assert_called_once_with(mock_event)
    component_manager.update_event.assert_called_once_with(
        event_queue_key, mock_event
    )
