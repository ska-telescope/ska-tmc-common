import time
from unittest import mock

import pytest
import tango

from ska_tmc_common import DeviceInfo, InputParameter
from ska_tmc_common.v2.event_manager import EventManager
from ska_tmc_common.v2.tmc_component_manager import TmcComponentManager
from tests.settings import MCCS_SUBARRAY_DEVICE, logger
from tests.test_component import TestTMCComponent

ATTRIBUTE_NAME = "state"
SUBSCRIPTION_CONFIGURATION = {MCCS_SUBARRAY_DEVICE: [ATTRIBUTE_NAME]}
COMPLETION_KEY = "is_subscription_completed"


class TestEventManager(EventManager):
    def state_event_callback(self, event):
        self.check_and_handle_event_error(event)


def is_expected_value_in_device_config_within_timeout(
    expected_value: str,
    device_name: str,
    event_manager: EventManager,
    timeout: int,
) -> bool:
    """Waits till the expected value is present in the device
        configuration.

    :param expected_value: expected attribute value
    :type expected_value: str
    :param device_name: tango device name
    :type device_name: str
    :param timeout: the function waits until this timeout.
    :type timeout: int
    :param event_manager: Event manager instance
    :type event_manager: EventManager
    :return: returns the success if the value is
        present in the configuration.
    :rtype: bool
    """
    start_time = time.time()
    elapsed_time: int = 0
    success: bool = False
    while not success:
        if event_manager.device_subscription_configuration.get(device_name):
            if (
                expected_value
                in event_manager.device_subscription_configuration.get(
                    device_name
                )
            ):
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
    dev_info = DeviceInfo(MCCS_SUBARRAY_DEVICE, True)  # exported device
    cm._component.update_device(dev_info)
    lp = cm.liveliness_probe_object
    lp.add_device(MCCS_SUBARRAY_DEVICE)
    event_manager = EventManager(cm)
    event_manager.state_event_callback = mock.Mock()
    event_manager.start_event_subscription(SUBSCRIPTION_CONFIGURATION)
    assert is_expected_value_in_device_config_within_timeout(
        ATTRIBUTE_NAME,
        MCCS_SUBARRAY_DEVICE,
        event_manager,
        5,
    )
    assert event_manager.device_subscription_configuration.get(
        MCCS_SUBARRAY_DEVICE
    ).get(COMPLETION_KEY)
    event_manager.state_event_callback.assert_called()
    event_manager.unsubscribe_events(MCCS_SUBARRAY_DEVICE)
    assert not event_manager.device_subscription_configuration.get(
        MCCS_SUBARRAY_DEVICE
    )


@pytest.mark.post_deployment
def test_late_event_subscription():
    cm = TmcComponentManager(
        _component=TestTMCComponent(logger=logger),
        _input_parameter=InputParameter(None),
        logger=logger,
    )
    dev_info = DeviceInfo(MCCS_SUBARRAY_DEVICE, True)  # exported device
    cm._component.update_device(dev_info)
    event_manager = EventManager(cm)
    cm.event_receiver_object = event_manager
    event_manager.state_event_callback = mock.Mock()
    event_manager.start_event_subscription(
        SUBSCRIPTION_CONFIGURATION, 5
    )  # device not available
    time.sleep(5)
    lp = cm.liveliness_probe_object
    lp.add_device(MCCS_SUBARRAY_DEVICE)
    assert is_expected_value_in_device_config_within_timeout(
        ATTRIBUTE_NAME,
        MCCS_SUBARRAY_DEVICE,
        event_manager,
        5,
    )
    assert event_manager.device_subscription_configuration.get(
        MCCS_SUBARRAY_DEVICE
    ).get(COMPLETION_KEY)
    event_manager.state_event_callback.assert_called()
    event_manager.unsubscribe_events(MCCS_SUBARRAY_DEVICE)
    assert not event_manager.device_subscription_configuration.get(
        MCCS_SUBARRAY_DEVICE
    )


@pytest.mark.post_deployment
def test_event_error_resubscription():
    cm = TmcComponentManager(
        _component=TestTMCComponent(logger=logger),
        _input_parameter=InputParameter(None),
        logger=logger,
    )
    dev_info = DeviceInfo(MCCS_SUBARRAY_DEVICE, True)  # exported device
    cm._component.update_device(dev_info)
    lp = cm.liveliness_probe_object
    lp.add_device(MCCS_SUBARRAY_DEVICE)
    event_manager = TestEventManager(cm, event_error_max_count=2)
    event_manager.start_event_subscription(SUBSCRIPTION_CONFIGURATION)
    assert is_expected_value_in_device_config_within_timeout(
        ATTRIBUTE_NAME,
        MCCS_SUBARRAY_DEVICE,
        event_manager,
        5,
    )
    assert event_manager.device_subscription_configuration.get(
        MCCS_SUBARRAY_DEVICE
    ).get(COMPLETION_KEY)
    initial_subscription_id = (
        event_manager.device_subscription_configuration.get(
            MCCS_SUBARRAY_DEVICE
        ).get(ATTRIBUTE_NAME)
    )
    admin_proxy = tango.DeviceProxy("dserver/test_device/01")
    admin_proxy.RestartServer()
    time.sleep(20)
    admin_proxy.RestartServer()
    time.sleep(20)
    current_subscription_id = (
        event_manager.device_subscription_configuration.get(
            MCCS_SUBARRAY_DEVICE
        ).get(ATTRIBUTE_NAME)
    )
    assert initial_subscription_id != current_subscription_id
