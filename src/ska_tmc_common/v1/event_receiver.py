"""
The event_receiver has the responsibility to receive events
from the sub devices managed by a TMC node.
"""

import threading
from logging import Logger
from time import sleep
from typing import Callable, Optional

import tango
from ska_control_model import AdminMode

from ska_tmc_common.dev_factory import DevFactory
from ska_tmc_common.device_info import DeviceInfo


# pylint: disable=duplicate-code
class EventReceiver:
    """
    The EventReceiver class has the responsibility to receive events
    from the sub devices managed by a TMC node. It subscribes to State,
    healthState and obsState attribute by default. To subscribe any additional
    attributes, the class should be sent an attribute_dictionary that contains
    the attribute names as keys and their handler methods as values.

    The Component Manager uses the handle events methods for the attribute of
    interest. For each of them a callback is defined.

    TBD: what about scalability? what if we have 1000 devices?
    """

    def __init__(
        self,
        component_manager,
        logger: Logger,
        attribute_dict: Optional[dict[str, Callable]] = None,
        max_workers: int = 1,
        proxy_timeout: int = 500,
        event_subscription_check_period: int = 1,
    ):
        self._thread = threading.Thread(target=self.run)
        self._stop = False
        self._logger = logger
        self._thread.daemon = True
        self._component_manager = component_manager
        self._proxy_timeout = proxy_timeout
        self._event_subscription_check_period = event_subscription_check_period
        self._max_workers = max_workers
        self._dev_factory = DevFactory()
        self.attribute_dictionary: dict[str, Callable] = attribute_dict or {
            "state": self.handle_state_event,
            "healthState": self.handle_health_state_event,
            "obsState": self.handle_obs_state_event,
            "adminMode": self.handle_admin_mode_event,
        }

    def start(self) -> None:
        """
        Checks if device is alive
        """
        if not self._thread.is_alive():
            self._thread.start()

    def stop(self) -> None:
        """
        Checks if device has stopped
        """
        self._stop = True

    #  pylint: disable=broad-exception-caught
    def run(self) -> None:
        """
        The run method for the Event Receiver thread. Runs in a loop to
        subscribe events on the devices.
        """
        with tango.EnsureOmniThread():
            while not self._stop:
                try:
                    if hasattr(self._component_manager, "devices"):
                        for dev_info in self._component_manager.devices:
                            self.submit_task(dev_info)
                    else:
                        dev_info = self._component_manager.get_device()
                        self.submit_task(dev_info)
                except Exception as exp:
                    self._logger.warning("Exception occurred: %s", exp)
                sleep(self._event_subscription_check_period)

    def submit_task(self, device_info: DeviceInfo) -> None:
        """Submits the task to the executor for the given device info object.

        :param device_info: DeviceInfo for the device on which events
            are to be subscribed.
        :type device_info: DeviceInfo

        :rtype: None
        """
        if device_info.last_event_arrived is None:
            self.subscribe_events(
                dev_info=device_info,
                attribute_dictionary=(self.attribute_dictionary),
            )

    def subscribe_events(
        self, dev_info: DeviceInfo, attribute_dictionary: dict[str, Callable]
    ) -> None:
        """A method to subscribe to attribute events from lower level devices.

        :param dev_info: The device info object of the given device.
        :type dev_info: DeviceInfo

        :param attribute_dictionary: A dictionary containing the attributes to
            subscribe to as keys and their handler functions as values.
        :type attribute_dictionary: dict[str, Callable]

        :rtype: None
        """
        try:
            proxy = self._dev_factory.get_device(dev_info.dev_name)
        except Exception as exception:
            self._logger.exception(
                "Exception occured while getting device proxy for "
                + "device %s: %s",
                dev_info,
                exception,
            )
        else:
            try:
                for attribute, callable_value in attribute_dictionary.items():
                    self._logger.info(
                        "Subscribing event for attribute: %s", attribute
                    )
                    proxy.subscribe_event(
                        attribute,
                        tango.EventType.CHANGE_EVENT,
                        callable_value,
                        stateless=True,
                    )
            except Exception as exception:
                self._logger.exception(
                    "Exception occured while subscribing to events "
                    + "for device %s: %s",
                    dev_info.dev_name,
                    exception,
                )

    def handle_health_state_event(self, event: tango.EventData) -> None:
        """
        It handles the health state events of different devices
        """
        if event.err:
            error = event.errors[0]
            self._logger.error(
                "Received error from device %s: %s %s",
                event.device.dev_name(),
                error.reason,
                error.desc,
            )
            self._component_manager.update_event_failure(
                event.device.dev_name()
            )
            return

        new_value = event.attr_value.value
        self._component_manager.update_device_health_state(
            event.device.dev_name(), new_value
        )

    def handle_state_event(self, event: tango.EventData) -> None:
        """
        It handles the state events of different devices
        """
        if event.err:
            error = event.errors[0]
            self._logger.error(
                "Reason :%s  Description %s", error.reason, error.desc
            )
            self._component_manager.update_event_failure(
                event.device.dev_name()
            )
            return

        new_value = event.attr_value.value
        self._component_manager.update_device_state(
            event.device.dev_name(), new_value
        )

    def handle_obs_state_event(self, event: tango.EventData) -> None:
        """
        It handles the observation state events of different devices
        """
        if event.err:
            error = event.errors[0]
            self._logger.error("%s\n %s", error.reason, error.desc)
            self._component_manager.update_event_failure(
                event.device.dev_name()
            )
            return

        new_value = event.attr_value.value
        self._component_manager.update_device_obs_state(
            event.device.dev_name(), new_value
        )

    def handle_admin_mode_event(
        self, event: tango.EventType.CHANGE_EVENT
    ) -> None:
        """Handle admin Mode change event"""
        if self._component_manager.is_admin_mode_enabled:
            if event.err:
                error = event.errors[0]
                error_msg = f"{error.reason},{error.desc}"
                self._logger.error(error_msg)
                self._component_manager.update_event_failure(
                    event.device.dev_name()
                )
                return
            new_value = event.attr_value.value
            self._logger.info(
                "Received an adminMode event with : %s for device: %s",
                new_value,
                event.device.dev_name(),
            )
            self._component_manager.update_device_admin_mode(
                event.device.dev_name(), new_value
            )
            self._logger.debug(
                "Admin Mode updated to :%s", AdminMode(new_value).name
            )
