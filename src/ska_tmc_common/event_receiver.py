"""
The event_receiver has the responsibility to receive events
from the sub devices managed by a TMC node.
"""

import threading
from concurrent import futures
from logging import Logger
from time import sleep

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
                            executor.submit(self.subscribe_events, dev_info)
                except Exception as e:
                    self._logger.warning("Exception occurred: %s", e)
                sleep(self._sleep_time)

    def subscribe_events(self, dev_info: DeviceInfo) -> None:
        """
        It subscribes the events from lower level devices
        """
        try:
            proxy = self._dev_factory.get_device(dev_info.dev_name)
        except Exception as e:
            self._logger.error(
                "Exception occurred while creating proxy: %s", e
            )
        else:
            try:
                # import debugpy; debugpy.debug_this_thread()
                proxy.subscribe_event(
                    "healthState",
                    tango.EventType.CHANGE_EVENT,
                    self.handle_health_state_event,
                    stateless=True,
                )
                proxy.subscribe_event(
                    "State",
                    tango.EventType.CHANGE_EVENT,
                    self.handle_state_event,
                    stateless=True,
                )
                if ("subarray" in dev_info.dev_name) and (
                    "leaf" not in dev_info.dev_name
                ):
                    proxy.subscribe_event(
                        "obsState",
                        tango.EventType.CHANGE_EVENT,
                        self.handle_obs_state_event,
                        stateless=True,
                    )
            except Exception as e:
                self._logger.debug(
                    "Event not working for device %s :%s", proxy.dev_name, e
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
