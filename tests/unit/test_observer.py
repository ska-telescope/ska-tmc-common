import logging
from unittest.mock import Mock

from ska_tmc_common.observer import (
    AttributeValueObserver,
    LongRunningCommandExceptionObserver,
)


def test_observer():
    command_callback_tracker = Mock()
    observable = Mock()
    observer = LongRunningCommandExceptionObserver(
        logging, command_callback_tracker, observable
    )
    observable.register_observer.assert_called_once()
    observer.notify("command_exception")
    command_callback_tracker.update_exception.assert_called_once()
    observer.notify(command_exception=True)
    assert command_callback_tracker.update_exception.call_count == 2
    observer.notify("attribute_value_change")
    assert command_callback_tracker.update_exception.call_count == 2

    observer = AttributeValueObserver(
        logging, command_callback_tracker, observable
    )
    assert observable.register_observer.call_count == 2
    observer.notify("attribute_value_change")
    command_callback_tracker.update_attr_value_change.assert_called_once()
    observer.notify(attribute_value_change=True)
    assert command_callback_tracker.update_attr_value_change.call_count == 2
    observer.notify("command_exception")
    assert command_callback_tracker.update_attr_value_change.call_count == 2
