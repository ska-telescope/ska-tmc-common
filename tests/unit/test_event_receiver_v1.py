"""A module to test the Event Receiver class"""

import time
from unittest.mock import Mock

import pytest
from ska_control_model import ObsState
from tango import DevState, EventData

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


def test_event_subscription_additional_attributes(tango_context):
    """Tests the event subscription on a tango device."""
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)

    cm = DummyComponentManager(logger)
    cm.add_device(SUBARRAY_DEVICE)
    cm.start_event_processing_threads()
    event_receiver = EventReceiver(cm, logger, attribute_list=["obsState"])
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


def test_event_subscription_default(tango_context):
    """Tests the event subscription on a tango device."""
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)

    cm = DummyComponentManager(logger)
    cm.add_device(SUBARRAY_DEVICE)
    cm.start_event_processing_threads()
    event_receiver = EventReceiver(cm, logger)
    event_receiver.start()

    subarray_device.SetDirectState(DevState.ON)
    start_time = time.time()
    while cm.get_device().state != DevState.ON:
        if time.time() - start_time > TIMEOUT:
            event_receiver.stop()
            pytest.fail(
                reason="Timeout occured while waiting for State event to be"
                + " received."
            )
    event_receiver.stop()


# WIP
# @pytest.mark.pt11
# @pytest.mark.parametrize("event_queue", ["adminMode"])
# def test_handle_admin_mode_event_when_disabled(event_queue):
#     # Initialize mocks
#     dev_factory = DevFactory()
#     subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
#
#     logger = Mock()
#     component_manager = DummyComponentManager(logger)
#     component_manager.add_device(SUBARRAY_DEVICE)
#     component_manager.is_admin_mode_enabled = False
#     component_manager.start_event_processing_threads()
#
#     event_receiver = EventReceiver(
#         component_manager=component_manager,
#         logger=logger,
#     )
#
#     # Create a mock Tango EventData object with error
#     mock_event = Mock(spec=EventData)
#     mock_event.err = True
#     mock_event.errors = [
#         MagicMock(reason="ErrorReason", desc="ErrorDescription")
#     ]
#     mock_event.device.dev_name.return_value = "test/device/1"
#     event_receiver.handle_event(mock_event)
#
#     subarray_device.SetDirectState(DevState.ON)
#     start_time = time.time()
#     while cm.get_device().state != DevState.ON:
#         if time.time() - start_time > TIMEOUT:
#             event_receiver.stop()
#             pytest.fail(
#                 reason="Timeout occured while waiting for State event to be"
#                        + " received."
#             )
#     event_receiver.stop()
#
#     logger.error.assert_not_called()
#     logger.info.assert_not_called()


@pytest.mark.parametrize(
    "event_method, event_queue_key",
    [
        ("handle_event", "state"),
        ("handle_event", "healthState"),
        ("handle_event", "obsState"),
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
    mock_event.attr_name = (
        f"ska_mid/tm_leaf_node/sdp_subarray01/{event_queue_key}"
    )

    # Dynamically call the method under test
    method_to_call = getattr(event_receiver, event_method)
    method_to_call(mock_event)

    component_manager.update_event.assert_called_once_with(
        event_queue_key, mock_event
    )
