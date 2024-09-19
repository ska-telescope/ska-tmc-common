"""Tests for EventCallback class"""

from tango import EventData

from ska_tmc_common import EventCallback


def callback(event_data: EventData):
    """Simple callback"""


def faulty_callback():
    """A callback without input"""


class DummyEventData:
    """Dummy event data class to test event callback"""

    def __init__(self, attr_name: str, data: str):
        self.attr_name = attr_name
        self.attr_value = data
        self.err = False
        self.errors = []


class DummyError:
    """Dummy Error class"""

    def __init__(self, reason: str, desc: str) -> None:
        self.reason = reason
        self.desc = desc


def test_event_callback_methods():
    """Test for methods in EventCallback"""
    event_callback = EventCallback(callback)
    dummy_data = DummyEventData("DummyAttr", "DummyVal")
    event_callback.push_event(dummy_data)
    assert len(event_callback.events) == 1
    events = event_callback.get_events()
    assert events[0] == dummy_data


def test_event_callback_push_event_exception():
    """Test for methods in EventCallback"""
    event_callback = EventCallback(faulty_callback)
    dummy_data = DummyEventData("DummyAttr", "DummyVal")
    event_callback.push_event(dummy_data)


def test_event_callback_with_error_event():
    """Test for error event in EventCallback"""
    event_callback = EventCallback(callback)
    dummy_data = DummyEventData("DummyAttr", "DummyVal")
    dummy_data.err = True
    dummy_data.errors.append(DummyError("Self induced", "Error occurred"))
    event_callback.push_event(dummy_data)
    assert len(event_callback.events) == 1
