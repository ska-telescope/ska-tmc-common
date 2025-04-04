import time
from unittest import mock

import pytest

from ska_tmc_common import DeviceInfo, InputParameter
from ska_tmc_common.v2.event_manager import EventManager
from ska_tmc_common.v2.tmc_component_manager import TmcComponentManager
from tests.settings import CSP_SUBARRAY_DEVICE, logger
from tests.test_component import TestTMCComponent

SUBSCRIPTION_CONFIGURATION = {CSP_SUBARRAY_DEVICE: ["state"]}


def is_expected_value_in_device_config_within_timeout(
    expected_value: str, device_name: str, device_config: dict, timeout: int
) -> bool:
    """Waits till the expected value is present in the device
        configuration.

    :param expected_value: expected attribute value
    :type expected_value: str
    :param device_name: tango device name
    :type device_name: str
    :param device_config: device configuration
    :type device_config: dict
    :param timeout: the function waits until this timeout.
    :type timeout: int
    :return: returns the success if the value is
        present in the configuration.
    :rtype: bool
    """
    start_time = time.time()
    elapsed_time: int = 0
    success: bool = False
    while not success:
        if device_config.get(device_name):
            if expected_value in device_config.get(device_name):
                success = True
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout:
            break
    return success


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
    assert is_expected_value_in_device_config_within_timeout(
        "state",
        CSP_SUBARRAY_DEVICE,
        event_manager.device_subscription_configuration,
        5,
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
    assert is_expected_value_in_device_config_within_timeout(
        "state",
        CSP_SUBARRAY_DEVICE,
        event_manager.device_subscription_configuration,
        5,
    )
    assert event_manager.device_subscription_configuration.get(
        CSP_SUBARRAY_DEVICE
    ).get("is_subscription_completed")
    event_manager.state_event_callback.assert_called()
    event_manager.unsubscribe_events(CSP_SUBARRAY_DEVICE)
    assert not event_manager.device_subscription_configuration.get(
        CSP_SUBARRAY_DEVICE
    )
