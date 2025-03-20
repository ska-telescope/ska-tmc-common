"""
The event_receiver has the responsibility to receive events
from the sub devices managed by a TMC node.
"""

import threading
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
    healthState  attribute by default. To subscribe any
    additional attributes, the class should be sent an
    attribute_tobe_subscribed that contains
    the attribute names

    TBD: what about scalability? what if we have 1000 devices?
    """

    def __init__(
        self,
        component_manager,
        logger: Logger,
        attribute_list: Optional[dict[str, Callable]] = None,
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
        self.attribute_tobe_subscribed: list[str] = attribute_list or [
            "state",
            "healthState",
        ]
        self.event_lock = threading._RLock()

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
                attribute_tobe_subscribed=(self.attribute_tobe_subscribed),
            )

    def subscribe_events(
        self,
        dev_info: DeviceInfo,
        attribute_tobe_subscribed: list[str],
    ) -> None:
        """A method to subscribe to attribute events from lower level devices.

        :param dev_info: The device info object of the given device.
        :type dev_info: DeviceInfo

        :param attribute_tobe_subscribed: A list containing the attributes to
            subscribe
        :type attribute_tobe_subscribed: list[str]

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
                for attribute in attribute_tobe_subscribed:
                    self._logger.info(
                        "Subscribing event for attribute: %s", attribute
                    )
                    proxy.subscribe_event(
                        attribute,
                        tango.EventType.CHANGE_EVENT,
                        self.handle_event,
                        stateless=True,
                    )
                    self.stop()
            except Exception as exception:
                self._logger.exception(
                    "Exception occured while subscribing to events "
                    + "for device %s: %s",
                    dev_info.dev_name,
                    exception,
                )

    def handle_event(self, event: tango.EventType.CHANGE_EVENT) -> None:
        """Submit event to callback for processing
        thus making tango bus free for next event handling"""
        with self.event_lock:

            attr_name = event.attr_name.split("/")[-1]
            if "#dbase=no" in attr_name:
                attr_name = attr_name.split("#")[0]
            self._component_manager.update_event(attr_name, event)
