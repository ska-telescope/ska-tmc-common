"""Simple component manager and event receiver classes"""
# pylint: disable=broad-exception-caught
import logging
import logging.config
import threading
import time
from functools import partial
from typing import Any, Dict, List

import tango
from ska_ser_logging.configuration import configure_logging

from ska_tmc_common.event_callback import EventCallback

configure_logging()
LOGGER = logging.getLogger(__name__)


class SimpleComponentManager:
    """Simple CM class"""

    def __init__(self, device_name: str, event_receiver: bool) -> None:
        self.device_name = device_name
        self._devices = [self.device_name]
        if event_receiver:
            self.event_receiver = SimpleEventReceiver(self)
            self.event_receiver.start()
        self.device_data_lock = threading.Lock()
        self.device_data: Dict[str, Dict[str, Any]] = {}
        LOGGER.info("Initialisation of ComponentManager complete")

    @property
    def devices(self) -> List:
        """Returns a list of devices."""
        return self._devices

    def get_device_data(self, device_name: str) -> Dict | None:
        """Simple get method"""
        with self.device_data_lock:
            return self.device_data.get(device_name, None)

    def process_event(
        self, device_name: str, attribute: str, value: Any
    ) -> None:
        """Simple method to process events."""
        with self.device_data_lock:
            if int(value) >= 8:
                time.sleep(10)
            if not self.device_data.get(device_name):
                self.device_data[device_name] = {}
            self.device_data[device_name][attribute] = value
            LOGGER.info(
                "Processed the event for: %s and attribute: %s with value: %s",
                device_name,
                attribute,
                value,
            )


class SimpleEventReceiver:
    """Simple event receiver class"""

    def __init__(self, component_manager: SimpleComponentManager) -> None:
        self.thread = threading.Thread(target=self.run)
        self._stop = False
        self.thread.daemon = True
        self.component_manager = component_manager
        self.device_attribute_event_ids: Dict[str, Dict[str, int]] = {}
        self.event_id_modification_lock = threading.Lock()
        self.event_callback = partial(
            EventCallback, component_manager=component_manager
        )
        LOGGER.info("Initialisation of EventReceiver complete")

    def start(self) -> None:
        """Start method"""
        if not self.thread.is_alive():
            self.thread.start()

    def stop(self) -> None:
        """
        Stops the event receiver
        """
        self._stop = True

    def run(self) -> None:
        """Run method"""
        with tango.EnsureOmniThread():
            while not self._stop:
                try:
                    for device in self.component_manager.devices:
                        device_proxy = tango.DeviceProxy(device)
                        self.subscribe_events(device_proxy)
                except Exception as exception:
                    LOGGER.warning("Exception occurred: %s", exception)
                time.sleep(0.5)

    def subscribe_events(self, device_proxy: tango.DeviceProxy) -> None:
        """Simple subscription method"""
        try:
            self.subscribe_to_event(
                device_proxy,
                "State",
                self.event_callback(callback_name="State"),
            )
            self.subscribe_to_event(
                device_proxy,
                "my_rw_attribute",
                self.event_callback(callback_name="RW"),
            )
            self.subscribe_to_event(
                device_proxy,
                "my_ro_attribute",
                self.event_callback(callback_name="RO"),
            )
        except Exception as exception:
            LOGGER.exception(
                "Exception occured while subscribing to event: %s", exception
            )

    def subscribe_to_event(
        self,
        device_proxy: tango.DeviceProxy,
        attribute_name: str,
        event_callback: Any,
    ) -> None:
        """Subscribe to the attribute event for the device with provided
        callback function. If the event is already subscribed to, return. If
        not, add the entry to the device_attribute_event_ids dictionary, with
        the subscription id.

        :param device_proxy: Device proxy of the device for which event has to
            be subscribed to.
        :type device_proxy: `tango.DeviceProxy`

        :param attribute_name: Attribute name for which the event has to be
            subscribed to.
        :type attribute_name: `str`

        :param event_callback: Callback to be used for processing event data
        :type event_callback: `Any`
        """
        if self.device_attribute_event_ids.get(
            device_proxy.dev_name(), {}
        ).get(attribute_name):
            LOGGER.info("Already subscribed to event.")
            self._stop = True
            return

        event_id = device_proxy.subscribe_event(
            attribute_name,
            tango.EventType.CHANGE_EVENT,
            event_callback,
            stateless=True,
        )

        self.set_device_attribute_event_ids(
            device_proxy.dev_name(), attribute_name, event_id
        )

    def set_device_attribute_event_ids(
        self, dev_name: str, attribute_name: str, event_id: int
    ) -> None:
        """Stores the value for attribute event id.

        :param dev_name: Device name for which the event id is being stored.
        :type dev_name: `str`
        :param attribute_name: Attribute name for which the event id has to be
            stored.
        :type attribute_name: `str`
        :param event_id: Event id for the event subscription
        :type event_id: `int`
        """
        with self.event_id_modification_lock:
            LOGGER.info(
                "Updating the device_attribute_event_ids dictionary with "
                + "following parameters: Device name - %s, attribute name - %s"
                + ", event id - %s",
                dev_name,
                attribute_name,
                event_id,
            )
            if not self.device_attribute_event_ids.get(dev_name):
                self.device_attribute_event_ids[dev_name] = {}

            self.device_attribute_event_ids[dev_name][
                attribute_name
            ] = event_id
        LOGGER.info(
            "Updated device_attribute_event_ids dictionary is: %s",
            self.device_attribute_event_ids,
        )
