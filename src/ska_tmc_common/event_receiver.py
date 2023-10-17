"""
The event_receiver has the responsibility to receive events
from the sub devices managed by a TMC node.
"""

import threading
from concurrent import futures
from logging import Logger
from time import sleep
from typing import Callable, Optional

import tango

from ska_tmc_common.dev_factory import DevFactory
from ska_tmc_common.device_info import DeviceInfo


class EventReceiver:
    """
    The EventReceiver class has the responsibility to receive events
    from the sub devices managed by a TMC node. It subscribes to State,
    healthState and obsState attribute. TO subscribe any additional attribute,
    the class should be inherited, override the `subscribe_events` method
    and implement appropriate event handler methods.

    The ComponentManager uses the handle events methods
    for the attribute of interest.
    For each of them a callback is defined.

    TBD: what about scalability? what if we have 1000 devices?

    """

    def __init__(
        self,
        component_manager,
        logger: Logger,
        attribute_dict: Optional[dict[str, Callable]] = None,
        max_workers: int = 1,
        proxy_timeout: int = 500,
        sleep_time: int = 1,
    ):
        self._thread = threading.Thread(target=self.run)
        self._stop = False
        self._logger = logger
        self._thread.daemon = True
        self._component_manager = component_manager
        self._proxy_timeout = proxy_timeout
        self._sleep_time = sleep_time
        self._max_workers = max_workers
        self._dev_factory = DevFactory()
        self.method_flag = True
        self.attribute_dictionary: dict[str, Callable] = attribute_dict or {
            "State": self.handle_state_event,
            "healthState": self.handle_health_state_event,
            "obsState": self.handle_obs_state_event,
        }

    def start(self) -> None:
        """
        checks if device is alive
        """
        if not self._thread.is_alive():
            self._thread.start()

    def stop(self) -> None:
        """
        checks if device has stopped
        """
        self._stop = True
        # self._thread.join()

    def run(self) -> None:
        """
        checks if device is running
        """
        with tango.EnsureOmniThread() and futures.ThreadPoolExecutor(
            max_workers=self._max_workers
        ) as executor:
            while not self._stop:
                try:
                    for dev_info in self._component_manager.devices:
                        if dev_info.last_event_arrived is None:
                            executor.submit(
                                self.subscribe_events,
                                dev_info=dev_info,
                                attribute_dictionary=(
                                    self.attribute_dictionary
                                ),
                            )
                except Exception as e:
                    self._logger.warning("Exception occurred: %s", e)
                sleep(self._sleep_time)

    def subscribe_events(
        self, dev_info: DeviceInfo, attribute_dictionary: dict[str, Callable]
    ) -> None:
        """A method to subscribe to attribute events from lower level devices.

        :param device_info: The device info object of the given device.
        :device_info dtype: DeviceInfo class object

        :param attribute_dictionary: A dictionary containing the attributes to
            subscribe to as keys and their handler functions as values.
        :attribute_dictionary dtype: dict[str, Callable]

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
                for attribute, callable in attribute_dictionary.items():
                    proxy.subscribe_event(
                        attribute,
                        tango.EventType.CHANGE_EVENT,
                        callable,
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
        It handles the health state of different devices
        """
        # import debugpy; debugpy.debug_this_thread()
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
        It handles the state of different devices
        """
        # import debugpy; debugpy.debug_this_thread()
        if event.err:
            error = event.errors[0]
            self._logger.error("%s %s", error.reason, error.desc)
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
        It handles the observation state of different devices
        """
        # import debugpy; debugpy.debug_this_thread()
        if event.err:
            error = event.errors[0]
            self._logger.error("%s %s", error.reason, error.desc)
            self._component_manager.update_event_failure(
                event.device.dev_name()
            )
            return

        new_value = event.attr_value.value
        self._component_manager.update_device_obs_state(
            event.device.dev_name(), new_value
        )
