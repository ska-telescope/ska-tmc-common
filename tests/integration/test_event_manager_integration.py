import time
from unittest import mock

import pytest

from ska_tmc_common import DeviceInfo, InputParameter
from ska_tmc_common.v2.event_manager import EventManager
from ska_tmc_common.v2.tmc_component_manager import TmcComponentManager
from tests.settings import CSP_SUBARRAY_DEVICE, logger
from tests.test_component import TestTMCComponent

SUBSCRIPTION_CONFIGURATION = {CSP_SUBARRAY_DEVICE: ["state"]}


@pytest.mark.post_deployment
def test_event_subscription():
    cm = TmcComponentManager(
        _component=TestTMCComponent(logger=logger),
        _input_parameter=InputParameter(None),
        logger=logger,
    )
    dev_info = DeviceInfo(CSP_SUBARRAY_DEVICE, True)  # exported device
    cm._component.update_device(dev_info)
    lp = cm.liveliness_probe_object
    lp.add_device(CSP_SUBARRAY_DEVICE)
    event_manager = EventManager(cm)
    event_manager.state_event_callback = mock.Mock()
    event_manager.start_event_subscription(SUBSCRIPTION_CONFIGURATION)
    time.sleep(2)
    assert "state" in event_manager.device_subscription_configuration.get(
        CSP_SUBARRAY_DEVICE
    )
    assert event_manager.device_subscription_configuration.get(
        CSP_SUBARRAY_DEVICE
    ).get("is_subscription_completed")
    event_manager.state_event_callback.assert_called()
    event_manager.unsubscribe_events(CSP_SUBARRAY_DEVICE)
    assert not event_manager.device_subscription_configuration.get(
        CSP_SUBARRAY_DEVICE
    )


@pytest.mark.post_deployment
def test_late_event_subscription():
    cm = TmcComponentManager(
        _component=TestTMCComponent(logger=logger),
        _input_parameter=InputParameter(None),
        logger=logger,
    )
    dev_info = DeviceInfo(CSP_SUBARRAY_DEVICE, True)  # exported device
    cm._component.update_device(dev_info)
    event_manager = EventManager(cm)
    event_manager.start_event_subscription(
        SUBSCRIPTION_CONFIGURATION, 10
    )  # device not available
    event_manager.state_event_callback = mock.Mock()
    time.sleep(10)
    lp = cm.liveliness_probe_object
    lp.add_device(CSP_SUBARRAY_DEVICE)
    time.sleep(2)
    assert "state" in event_manager.device_subscription_configuration.get(
        CSP_SUBARRAY_DEVICE
    )
    assert event_manager.device_subscription_configuration.get(
        CSP_SUBARRAY_DEVICE
    ).get("is_subscription_completed")
    event_manager.state_event_callback.assert_called()
    event_manager.unsubscribe_events(CSP_SUBARRAY_DEVICE)
    assert not event_manager.device_subscription_configuration.get(
        CSP_SUBARRAY_DEVICE
    )
