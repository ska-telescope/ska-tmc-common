"""
This module contains event management functionality.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import TYPE_CHECKING, Optional

import tango
from ska_ser_logging import configure_logging

from ska_tmc_common.dev_factory import DevFactory
from ska_tmc_common.log_manager import LogManager

if TYPE_CHECKING:
    from tmc_component_manager import (
        TmcComponentManager,
        TmcLeafNodeComponentManager,
    )

LOGGER = logging.getLogger("EventManager")
COMPLETION_INDICATOR_KEY = "is_subscription_completed"
SUBSCRITPTION_ID_KEY = "subscription_id"
EVENT_MANAGER_THREAD_NAME_PREFIX = "event_manager_thread_"
TIMER_THREAD_NAME_PREFIX = "event_timer_thread_"
API_EVENT_TIMEOUT = "API_EventTimeout"
EVENT_ERROR_DESC = "Event channel is not responding anymore"

configure_logging()


class EventManager:
    """
    This class provides necessary functions to manage event subscriptions.
    """

    def __init__(
        self,
        component_manager: TmcComponentManager | TmcLeafNodeComponentManager,
        subscription_configuration: Optional[dict[str, list]] = None,
        logger: logging.Logger = LOGGER,
        stateless: bool = True,
        event_subscription_check_period: int = 1,
        event_error_max_count: int = 10,
    ) -> None:
        """This method initialises the event manager class instances with
        necessary configurations.

        :param component_manager: The instance of component manager.
        :type component_manager: TmcComponentManager,
            TmcLeafNodeComponentManager.
        :param subscription_configuration: This parameter contains the detail
            of devices and their attributes to be subscribed, defaults to {}.
            For Example: {"device_name":["attribute1","attribute2"]}.
        :param logger: This parameter contains instance of logger that would
            be used to log necessary information/exceptions occured during
            the process of subscription, defaults to Logger instance.
        :type logger: loggging.Logger
        :param stateless: This sets the stateless flag used in subscribe
            events, defaults to True.
        :type stateless: bool
        :param event_subscription_check_period: This is the interval time
            between subscription retries, defaults to 1 second.
        :type event_subscription_check_period: int
        :param event_error_max_count: This is maximum tolerable count for
            API EventTimeout error.
        :type event_error_max_count: int
        """
        self.__logger: logging.Logger = logger
        self.__device_subscription_configuration: (
            dict[str, dict[int, bool]] | dict
        ) = {}
        self.__subscription_configuration: dict[str, list] = (
            subscription_configuration
        )
        self.__device_factory: DevFactory = DevFactory()
        self.__component_manager: (
            TmcComponentManager | TmcLeafNodeComponentManager
        ) = component_manager
        self.__stateless_flag: bool = stateless
        self.__log_manager: LogManager = LogManager(10)
        self.__timed_out: bool = False
        self.__timer_threads: dict[str, threading.Timer] | dict = {}
        self.__pending_configuration: dict[str, list] = {}
        self.__event_thread: Optional[threading.Thread] = None
        self.__error_handling_thread: Optional[threading.Thread] = None
        self.__event_subscription_check_period = (
            event_subscription_check_period
        )
        self.__device_error_tracking: dict = {}
        self.__event_error_max_count: int = event_error_max_count
        self.__pending_configuration_lock: threading.RLock = threading.RLock()
        self.__device_subscription_configuration_lock: threading.RLock = (
            threading.RLock()
        )
        self.__subscription_configuration_lock: threading.RLock = (
            threading.RLock()
        )
        self.__device_error_tracking_lock: threading.RLock = threading.RLock()

    @property
    def pending_configuration(self) -> dict[str, list]:
        """This method provides the pending configuration.

        :return: This method returns the pending subscription configurations.
        :rtype: dict[str, list]
        """
        with self.__pending_configuration_lock:
            return self.__pending_configuration

    @pending_configuration.setter
    def pending_configuration(self, configuration: dict[str, list]) -> None:
        """This method sets the pending configuration dictionary.

        :param configuration: This parameter contains dictionary with pending
            configruation.
        :type configuration: dict[str,list]
        """
        with self.__pending_configuration_lock:
            self.__pending_configuration = configuration

    @property
    def stateless_flag(self) -> bool:
        """This method provides the stateless flaf for event subscription.

        :return: This returns the value of stateless flag.
        :rtype: bool
        """
        return self.__stateless_flag

    @stateless_flag.setter
    def stateless_flag(self, updated_flag: bool):
        """This method updates the stateless flag required for event
        subscription.

        :param updated_flag: This contains the boolean flag for stateless
            parameter.
        :type updated_flag: bool
        """
        self.__stateless_flag = updated_flag

    @property
    def subscription_configruation(self) -> dict[str, list]:
        """This method provides the subscription configuration provided.

        :return: This method returns the subscription configuration.
        :rtype: dict[str, list]
        """
        with self.__subscription_configuration_lock:
            return self.__subscription_configuration

    @property
    def device_subscription_configuration(
        self,
    ) -> dict[str, dict[int, bool]] | dict:
        """This method provides the instanc of device subscription
        configuration dictionary.

        :return: This method returns the value of device subscription
            configuration variable.
        :rtype: dict[str, dict[int, bool]],dict
        """
        with self.__device_subscription_configuration_lock:
            return self.__device_subscription_configuration

    @device_subscription_configuration.setter
    def device_subscription_configuration(
        self, updated_configuration: dict
    ) -> None:
        """This method is used to set the device subscription configuration
        dictionary.

        :param updated_configuration: This contains the configuration to be
            updated in variable device subscription configuration.
        :type updated_configuration: dict
        """
        with self.__device_subscription_configuration_lock:
            self.__device_subscription_configuration = updated_configuration

    @property
    def device_error_tracking(self) -> None:
        """This method returns dictionary with device errors."""
        with self.__device_error_tracking_lock:
            return self.__device_error_tracking

    def set_timeout(self) -> None:
        """Sets the timeout flag."""
        self.__timed_out = True

    def start_timer(self, name: str, timeout: int = 1000) -> None:
        """This method starts a timer thread which updates timeout flag
            once it is completed.

        :param name: The name of the the timer thread.
        :type name: str
        :param timeout: Timeout till when the subscriptions will be retired.
        :type timeout: int
        """
        self.__timer_threads.update(
            {name: threading.Timer(timeout, self.set_timeout)}
        )

    def stop_timer(self, name: str) -> None:
        """This method stops the timer thread running.

        :param name: The name of the timer thread which needs to be stopped.
        :type name: str
        """
        if self.__timer_threads.get(name):
            self.__timer_threads.get(name).cancel()

    def start_event_subscription(
        self,
        subscription_configuration: Optional[dict[str, list]] = None,
        timeout: int = 1000,
    ) -> None:
        """This method starts a thread to subscribe events.

        :param subscription_configuration: This is optional parameter,
            if user wants to start thread with different configuration.
        :type subscription_configuration: dict[str, list], optional
        :param timeout: The duration till when it will try to subscribe,
            defaults to 1000 seconds
        :type timeout: int
        """
        subscription_configuration = (
            subscription_configuration.copy()
            or self.subscription_configruation
        )
        self.__event_thread = threading.Thread(
            target=self.subscribe_events,
            args=(subscription_configuration, timeout),
            name=EVENT_MANAGER_THREAD_NAME_PREFIX + str(time.time()),
            daemon=True,
        )
        self.__event_thread.start()

    def unsubscribe_events(
        self, device_name: str, attribute_names: Optional[list] = None
    ) -> None:
        """This method unsubcribes the events of the specified device name
        or some attributes under that device name.

        :param device_name: This variable consists of device name whose events
            needs to be unsubscribed.
        :type device_name: str
        :param attribute_names: This list contains names of specific attributes
            that needs to be unsubscribed.
        :type attribute_names: list, optional
        """
        attribute_list = attribute_names or list(
            self.device_subscription_configuration.get(device_name).keys()
        )

        proxy = self.__device_factory.get_device(device_name)
        for attribute_name in attribute_list:
            if attribute_name != COMPLETION_INDICATOR_KEY:
                proxy.unsubscribe_event(
                    self.device_subscription_configuration.get(device_name)
                    .get(attribute_name)
                    .get(SUBSCRITPTION_ID_KEY)
                )
            self.device_subscription_configuration.get(device_name).pop(
                attribute_name
            )
        if (
            len(
                list(
                    self.device_subscription_configuration.get(
                        device_name
                    ).keys()
                )
            )
            == 1
            and COMPLETION_INDICATOR_KEY
            in self.device_subscription_configuration.get(device_name).keys()
        ):
            self.device_subscription_configuration.get(device_name).pop(
                COMPLETION_INDICATOR_KEY
            )

    def init_device_subscription_configuration(self, device_name: str) -> None:
        """Initialisation of device configuration dictionary.

        :param device_name: device name.
        :type device_name: str
        """
        if not self.device_subscription_configuration.get(device_name):
            self.device_subscription_configuration.update({device_name: {}})

    def update_device_subscription_configuration(
        self,
        device_name: str,
        attribute_name: Optional[str] = None,
        subscription_id: Optional[int] = None,
        is_subscription_completed: Optional[bool] = None,
    ) -> None:
        """This method updates device_subscription_configuration dictionary
        with the provided values.

        :param device_name: tango device FQDN.
        :type device_name: str
        :param attribute_name: Attribute name under provided device.
        :type attribute_name: str, optional
        :param subscription_id: Subscription ID of attribute after successful
            completion.
        :type subscription_id: int, optional
        :param is_subscription_completed: This flag is set once all the
            subscription is completed.
        :type is_subscription_completed: bool, optional
        """
        if attribute_name and subscription_id:
            self.device_subscription_configuration.get(device_name).update(
                {attribute_name: {SUBSCRITPTION_ID_KEY: subscription_id}}
            )
        elif device_name and is_subscription_completed:
            self.device_subscription_configuration.get(device_name).update(
                {COMPLETION_INDICATOR_KEY: is_subscription_completed}
            )

    def get_device_proxy(self, device_name: str) -> tango.DeviceProxy:
        """This method creates device proxy for the provided device name.

        :param device_name: Tango device FQDN.
        :type device_name: str
        :return: Returns device proxy
        :rtype: tango.DeviceProxy
        """
        try:
            proxy = self.__device_factory.get_device(device_name)
            return proxy
        except Exception as exception:
            if self.__log_manager.is_logging_allowed(f"{device_name}_log"):
                self.__logger.error(
                    "Following exception occured: %s "
                    "while connecting with device : %s",
                    exception,
                    device_name,
                )
            return None

    def subscribe_events(
        self, subscription_configuration: dict[str, list], timeout: int = 1000
    ) -> None:
        """This functions utilises the subscription configuration provided
        and subscribes to the attributes present in them.
        The function updates device_subscription_configuration dictionary
        with the details of sucess and failure.

        :param subscription_configuration: The variable contains the detail
            of devices and their attributes to be subscribed.
            For Example: {"device_name":["attribute1","attribute2"]}.
        :type subscription_configuration: dict[str, list]
        :param timeout: The duration till when it will try to subscribe,
            defaults to 1000 seconds
        :type timeout: int
        """
        with tango.EnsureOmniThread():
            timer_thread_name: str = TIMER_THREAD_NAME_PREFIX + str(
                time.time()
            )
            self.start_timer(timer_thread_name, timeout)
            check_device_responsiveness = (
                self.__component_manager.check_device_responsiveness
            )
            while subscription_configuration and not self.__timed_out:
                for (
                    device_name,
                    attribute_names,
                ) in subscription_configuration.items():
                    subscription_completion: list = []
                    self.init_device_subscription_configuration(device_name)
                    if not check_device_responsiveness(device_name):
                        continue
                    proxy = self.get_device_proxy(device_name)
                    if not proxy:
                        continue
                    for attribute_name in attribute_names:
                        try:
                            if attribute_name in list(
                                self.device_subscription_configuration.get(
                                    device_name
                                ).keys()
                            ):
                                continue
                            subscription_id: int = proxy.subscribe_event(
                                attribute_name,
                                tango.EventType.CHANGE_EVENT,
                                getattr(
                                    self,
                                    f"{attribute_name.lower()}_event_callback",
                                ),
                                stateless=self.stateless_flag,
                            )
                            self.update_device_subscription_configuration(
                                device_name, attribute_name, subscription_id
                            )
                            subscription_completion.append(True)
                        except Exception as exception:
                            if self.__log_manager.is_logging_allowed(
                                f"{attribute_name}_log"
                            ):
                                self.__logger.error(
                                    "Following exception occured: %s"
                                    "while subscribing to attribute : %s"
                                    + "of device: %s",
                                    exception,
                                    attribute_name,
                                    device_name,
                                )
                            subscription_completion.append(False)
                    self.update_device_subscription_configuration(
                        device_name,
                        is_subscription_completed=all(subscription_completion),
                    )
                self.remove_subscribed_devices(
                    self.device_subscription_configuration,
                    subscription_configuration,
                )
                time.sleep(self.__event_subscription_check_period)
            if subscription_configuration:
                self.pending_configuration.update(subscription_configuration)
            self.stop_timer(timer_thread_name)

    def remove_subscribed_devices(
        self,
        device_subscription_configuration: dict,
        subscription_configuration: dict,
    ) -> None:
        """This method removes the devices from the configuration data.

        :param device_subscription_configuration: This parameter contains
            device subscription configuration.
        :type device_subscription_configuration: dict
        :param subscription_configuration: This parameter contains the detail
            of devices and their attributes to be subscribed.
        :type subscription_configuration: dict
        """

        for (
            device_name,
            configuration,
        ) in device_subscription_configuration.items():
            if configuration.get(COMPLETION_INDICATOR_KEY):
                subscription_configuration.pop(device_name, None)

    def subscribe_pending_events(self, device_name: str):
        """This method checks for pending subscriptions for the
        device.

        :param device_name: tango device FQDN.
        :type device_name: str
        """
        if self.pending_configuration.get(device_name):
            self.start_event_subscription(
                {device_name: self.pending_configuration.get(device_name)}
            )

    def device_avaiability_callback(self, device_name: str) -> None:
        """This method is called once device is available back again to
        subscribe events if it that is pending.

        :param device_name: tango device FQDN which is available again.
        :type device_name: str
        """
        self.subscribe_pending_events(device_name)

    def get_device_and_attribute_name(self, attribute_fqdn: str) -> tuple[str]:
        """This method provides device and attribute name.

        :param attribute_fqdn: Full attribute FQDN from event data.
        :type attribute_fqdn: str
        :return: Returns device name and attribue name
        :rtype: tuple[str]
        """
        attribute_name = attribute_fqdn.split("/")[-1]
        remove_attribute_name_with_slash = "/" + attribute_name
        device_name = attribute_fqdn.replace(
            remove_attribute_name_with_slash, ""
        )
        if not self.device_subscription_configuration.get(device_name):
            device_name = device_name.split("/", 3)[-1]
        return device_name, attribute_name

    def handle_event_error(self, event: tango.EventData) -> None:
        """This method handles the event error by tracking

        :param event: change event data with error.
        :type event: tango.EventData
        """
        with tango.EnsureOmniThread():
            if self.__log_manager.is_logging_allowed(
                f"{event.attr_name}_error_log"
            ):
                self.__logger.error("Change event error: %s", event.errors)
            if (
                event.errors[0].reason == API_EVENT_TIMEOUT
                and EVENT_ERROR_DESC in event.errors[0].desc
            ):
                device_name, attribute_name = (
                    self.get_device_and_attribute_name(event.attr_name)
                )
                if device_name not in self.device_error_tracking:
                    self.device_error_tracking.update(
                        {device_name: {attribute_name: 1}}
                    )
                elif attribute_name not in self.device_error_tracking.get(
                    device_name
                ):
                    self.device_error_tracking.get(device_name).update(
                        {attribute_name: 1}
                    )
                else:
                    error_count: int = self.device_error_tracking.get(
                        device_name
                    ).get(attribute_name)
                    if error_count >= self.__event_error_max_count:
                        self.unsubscribe_events(device_name, [attribute_name])
                        self.subscribe_events({device_name: [attribute_name]})
                        self.device_error_tracking.get(device_name).pop(
                            attribute_name
                        )
                    else:
                        self.device_error_tracking[device_name][
                            attribute_name
                        ] += 1

    def check_and_handle_event_error(self, event: tango.EventData) -> bool:
        """Checks event error and handles the API timeout error if it
        persists.

        :param event: Change event data
        :type event: tango.EventData
        :return: Returns True if event data has error,
            else returns False.s
        :rtype: bool
        """
        if not event.err:
            return False
        self.__error_handling_thread = threading.Thread(
            target=self.handle_event_error,
            args=(event,),
        )
        self.__error_handling_thread.start()
        return True
