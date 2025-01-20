from unittest.mock import Mock

import pytest

from ska_tmc_common.observable import Observable


def test_observable():
    observer = Mock()
    observable = Observable()
    observable.register_observer(observer)
    assert observable.observers == [observer]
    observable.notify_observers("attribute_value_change")
    observer.notify.assert_called_with("attribute_value_change")
    with pytest.raises(AssertionError):
        observer.notify.assert_called_with("command_exception")
    observable.deregister_observer(observer)
    assert observable.observers == []
