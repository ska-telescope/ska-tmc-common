"""
This module provided a reference implementation of a BaseComponentManager.

It is provided for explanatory purposes, and to support testing of this
package.
"""

# pylint: disable=unused-argument

import json
import threading
import time
from logging import Logger
from queue import Empty, Queue
from typing import Any, Callable, Dict, Optional, Union

import tango
from ska_tango_base.control_model import AdminMode, HealthState, ObsState
from ska_tango_base.executor import TaskExecutorComponentManager

from ska_tmc_common.device_info import (
    DeviceInfo,
    DishDeviceInfo,
    SubArrayDeviceInfo,
)
from ska_tmc_common.enum import LivelinessProbeType, TimeoutState
from ska_tmc_common.input import InputParameter
from ska_tmc_common.observable import Observable
from ska_tmc_common.op_state_model import TMCOpStateModel
from ska_tmc_common.timeout_callback import TimeoutCallback
from ska_tmc_common.v1.event_receiver import EventReceiver
from ska_tmc_common.v1.liveliness_probe import (
    MultiDeviceLivelinessProbe,
    SingleDeviceLivelinessProbe,
)


class TmcComponent:
    """
    This class provides a reference implementation of BaseComponentManager.
    """

    def __init__(self, logger: Logger):
        self.logger = logger
        # _health_state is never changing. Setter not implemented
        self._health_state = HealthState.OK
        self._devices = []

    def get_device(self, device_name):
        """
        Retrieve information about a specific device.
        This is a base method that should be implemented by derived classes.
        :raises NotImplementedError: Not implemented error
        """
        raise NotImplementedError("This method must be inherited!")

    def update_device(self, dev_info):
        """
        Base method for update_device method for different nodes
        :raises NotImplementedError: Not implemented error
        """
        raise NotImplementedError("This method must be inherited!")

    def update_device_exception(self, device_info, exception):
        """
        Base method for update_device_exception method for different nodes
        :raises NotImplementedError: Not implemented error
        """
        raise NotImplementedError("This method must be inherited!")

    def to_json(self) -> str:
        """
        Base method for to_json method for different nodes
        :return: json
        """
        return json.dumps(self.to_dict())

    def to_dict(self):
        """
        Base method for to_dict method for different nodes
        :raises NotImplementedError: Not implemented error
        """
        raise NotImplementedError("This method must be inherited!")


# pylint: disable=abstract-method
# Disabled as this is also a abstract class and has parent class from
# base class
class BaseTmcComponentManager(TaskExecutorComponentManager):
    """
    This class manages obsstates , commands and various checks
    on TMC components.
    """

    def __init__(
        self,
        logger: Logger,
        *args,
        _event_receiver: bool = False,
        communication_state_callback: Optional[Callable] = None,
        component_state_callback: Optional[Callable] = None,
        proxy_timeout: int = 500,
        event_subscription_check_period: int = 1,
        liveliness_check_period: int = 1,
        **kwargs,
    ):
        super().__init__(
            logger,
            communication_state_callback,
            component_state_callback,
        )
        self.event_receiver = _event_receiver
        self._is_admin_mode_enabled: bool = True
        self.proxy_timeout = proxy_timeout
        self.event_subscription_check_period = event_subscription_check_period
        self.liveliness_check_period = liveliness_check_period
        self.op_state_model = TMCOpStateModel(logger, callback=None)
        self.lock = threading.Lock()
        self.rlock = threading._RLock()
        if self.event_receiver:
            evt_sub_check_period = event_subscription_check_period
            self.event_receiver_object = EventReceiver(
                self,
                logger=logger,
                proxy_timeout=proxy_timeout,
                event_subscription_check_period=evt_sub_check_period,
            )
        self.timer_object = None
        self.liveliness_probe_object: (
            Union[SingleDeviceLivelinessProbe, MultiDeviceLivelinessProbe]
            | None
        ) = None
        self._command_id: str = ""
        self.observable = Observable()
        self._device = None
        self.event_queues = {}
        self._stop_thread: bool = False
        self.event_queues: Dict[str, Queue] = {
            "obsState": Queue(),
            "longRunningCommandResult": Queue(),
            "adminMode": Queue(),
            "healthState": Queue(),
            "state": Queue(),
        }
        self.event_processing_methods: Dict[
            str, Callable[[str, Any], None]
        ] = {
            "healthState": "update_device_health_state",
            "state": "update_device_state",
            "adminMode": "update_device_admin_mode",
            "obsState": "update_device_obs_state",
            "longRunningCommandResult": "update_command_result",
        }

    @property
    def command_id(self) -> str:
        """
        Read method for reading command id used for error propagation.
        :return: command_id
        """
        with self.lock:
            return self._command_id

    @command_id.setter
    def command_id(self, value: str) -> None:
        """Sets the command id used for error propagation."""
        with self.lock:

            self._command_id = value

    @property
    def is_admin_mode_enabled(self):
        """
        Return the admin mode enabled flag.

        :return: admin mode enabled flag
        :rtype: bool
        """
        with self.rlock:
            return self._is_admin_mode_enabled

    @is_admin_mode_enabled.setter
    def is_admin_mode_enabled(self, value):
        """
        Set the admin mode enabled flag.

        :param value: admin mode enabled flag
        :type value: bool
        :raises ValueError: If the provided value is not a boolean
        """
        if not isinstance(value, bool):
            raise ValueError("is_admin_mode_enabled must be a boolean value.")
        with self.rlock:
            self._is_admin_mode_enabled = value

    def get_device(self) -> DeviceInfo:
        """
        Return the device info out of the monitoring loop with name device_name
        :return: a device info
        :rtype: DeviceInfo
        """
        return self._device

    def is_command_allowed(self, command_name: str):
        """
        Checks whether this command is allowed
        It checks that the device is in a state to perform this command

        :param command_name: command_name
        :type command_name: str

        :rtype: boolean
        :raises NotImplementedError: raise not implemented error
        """
        raise NotImplementedError(
            "is_command_allowed is abstract; method must be implemented in \
            a subclass!"
        )

    def start_liveliness_probe(
        self, liveliness_probe_type: LivelinessProbeType
    ) -> None:
        """Starts Liveliness Probe for the given device.

        :param liveliness_probe_type: enum of class LivelinessProbeType
        """
        if liveliness_probe_type == LivelinessProbeType.SINGLE_DEVICE:
            if not self.liveliness_probe_object:
                self.liveliness_probe_object = SingleDeviceLivelinessProbe(
                    self,
                    logger=self.logger,
                    proxy_timeout=self.proxy_timeout,
                    liveliness_check_period=self.liveliness_check_period,
                )

            self.liveliness_probe_object.start()

        elif liveliness_probe_type == LivelinessProbeType.MULTI_DEVICE:
            if not self.liveliness_probe_object:
                self.liveliness_probe_object = MultiDeviceLivelinessProbe(
                    self,
                    logger=self.logger,
                    proxy_timeout=self.proxy_timeout,
                    liveliness_check_period=self.liveliness_check_period,
                )
            self.liveliness_probe_object.start()
        else:
            self.logger.warning("Liveliness Probe is not running")

    def stop_liveliness_probe(self) -> None:
        """Stops the liveliness probe"""
        if self.liveliness_probe_object:
            self.liveliness_probe_object.stop()

    def start_event_receiver(self) -> None:
        """Starts the Event Receiver for given device"""
        if self.event_receiver:
            self.event_receiver_object.start()

    def stop_event_receiver(self) -> None:
        """Stops the Event Receiver"""
        if self.event_receiver:
            self.event_receiver_object.stop()

    #  pylint: disable=broad-exception-caught
    def start_timer(
        self, timeout_id: str, timeout: int, timeout_callback: TimeoutCallback
    ) -> None:
        """Starts a timer for the command execution which will run for given
        amount of seconds. After the timer runs out, it will execute the
        task failed method.

        :param timeout_id: Id for TimeoutCallback class object.

        :param timeout: Interval value for the Timer

        :param timeout_callback: An instance of TimeoutCallback class that acts
                    as a callable functions to call in the event of timeout.
        """
        try:
            self.timer_object = threading.Timer(
                interval=timeout,
                function=self.timeout_handler,
                args=[timeout_id, timeout_callback],
            )
            self.logger.info(f"Starting timer for id : {timeout_id}")
            self.timer_object.start()
        except threading.ThreadError as thread_error:
            self.logger.info(f"Issue for  id : {timeout_id}")
            self.logger.exception(
                "Threading error occurred while starting the thread : %s",
                thread_error,
            )
        except Exception as exp_msg:
            self.logger.info(f"Issue for  id : {timeout_id}")
            self.logger.exception(
                "Exception occured while starting the timer thread : %s",
                exp_msg,
            )

    def update_device_admin_mode(
        self, device_name: str, admin_mode: AdminMode
    ) -> None:
        """
        Update a monitored device admin mode,
        and call the relative callbacks if available
        :param device_name: Name of the device on which admin mode is updated
        :type device_name: str
        :param admin_mode: admin mode of the device
        :type admin_mode: AdminMode
        """
        self.logger.info("Admin Mode value updated on device: %s", device_name)
        with self.rlock:
            dev_info = self.get_device()
            dev_info.adminMode = admin_mode
            dev_info.last_event_arrived = time.time()
            dev_info.update_unresponsive(False)

    #  pylint: enable=broad-exception-caught
    def timeout_handler(
        self, timeout_id: str, timeout_callback: TimeoutCallback
    ) -> None:
        """Updates the timeout callback to reflect timeout failure.

        :param timeout_id: Id for TimeoutCallback class object.

        :param timeout_callback: An instance of TimeoutCallback class that acts
                    as a callable functions to call in the event of timeout.
        """
        self.logger.info(f"Timeout occured for id : {timeout_id}")
        timeout_callback(
            timeout_id=timeout_id, timeout_state=TimeoutState.OCCURED
        )

    def stop_timer(self) -> None:
        """Stops the timer for command execution"""
        self.logger.info("Stopping timer %s", self.timer_object)
        self.timer_object.cancel()

    def update_event(self, event_type, event):
        """Updates event in respective queue"""
        self.event_queues[event_type].put(event)

    def process_event(self, attribute_name: str) -> None:
        """Process the given attribute's event using the data from the
        event_queues and invoke corresponding process method.

        :param attribute_name: Name of the attribute for which event is to be
            processed
        :type attribute_name: str


        """
        while not self._stop_thread:
            try:
                event_data = self.event_queues[attribute_name].get(
                    block=True, timeout=0.1
                )
                if not self.check_event_error(
                    event_data, f"{attribute_name}_Callback"
                ):
                    # self.event_processing_methods[attribute_name](
                    #     event_data.device.dev_name(),
                    #     event_data.attr_value.value,
                    # )

                    method_name = self.event_processing_methods[attribute_name]
                    if hasattr(self, method_name):
                        method = getattr(self, method_name)
                        method(
                            event_data.device.dev_name(),
                            event_data.attr_value.value,
                        )
                    else:
                        self.logger.error(
                            "Method %s not found in the current class"
                            " or child class.",
                            method_name,
                        )
            except Empty:
                # If an empty exception is raised by the Queue, we can
                # safely ignore it.
                pass
            except KeyError as key_error:
                # Handling missing keys in the event processing dictionary
                self.logger.error(f"Key error: {key_error} ")
            except AttributeError as attr_error:
                # Handling issues with dynamic method resolution
                self.logger.error(f"Attribute error: {attr_error} ")
            except Exception as exception:  # pylint: disable=broad-except
                self.logger.error(exception)
        self.logger.debug("Process event thread stopped")

    def check_event_error(self, event: tango.EventData, callback: str):
        """Method for checking event error."""
        if event.err:
            error = event.errors[0]
            self.logger.error(
                "Error occurred on %s for device: %s - %s, %s",
                callback,
                event.device.dev_name(),
                error.reason,
                error.desc,
            )

            if hasattr(self, "update_event_failure"):
                update_event_failure_method = getattr(
                    self, "update_event_failure"
                )
                if callable(update_event_failure_method):
                    # If callable, execute the method
                    update_event_failure_method(event.device.dev_name())
                else:
                    # Log error if method is not callable or not found
                    self.logger.error(
                        "The attribute 'update_event_failure' is "
                        "either not defined or not callable. "
                    )
            return True
        return False


class TmcComponentManager(BaseTmcComponentManager):
    """
    A component manager for The TMC node component.

    It supports:

    * Monitoring its component, e.g. detect that it has been turned off
      or on

    * Fetching the latest SCM indicator values of the components periodically
      and trigger various aggregation logic

    * Receiving the change events from the component
    """

    def __init__(
        self,
        _input_parameter: InputParameter,
        logger: Logger,
        *args,
        _component: Optional[TmcComponent] = None,
        _liveliness_probe: LivelinessProbeType = (
            LivelinessProbeType.MULTI_DEVICE
        ),
        _event_receiver: bool = True,
        communication_state_callback: Optional[Callable] = None,
        component_state_callback: Optional[Callable] = None,
        proxy_timeout: int = 500,
        event_subscription_check_period: int = 1,
        liveliness_check_period: int = 1,
        **kwargs,
    ):
        """
        Initialise a new ComponentManager instance.

        :param logger: a logger for this component manager
        :param _component: allows setting of the component to be
            managed; for testing purposes only
        """
        super().__init__(
            logger,
            _event_receiver,
            communication_state_callback,
            component_state_callback,
            proxy_timeout,
            event_subscription_check_period,
            liveliness_check_period,
            *args,
            **kwargs,
        )
        self._component = _component or TmcComponent(logger)
        self._devices = []
        self._input_parameter = _input_parameter
        self.start_liveliness_probe(_liveliness_probe)

    def reset(self) -> None:
        """
        Method to reset components
        """

    # pylint: disable=protected-access
    @property
    def devices(self) -> list:
        """
        Return the list of the monitored devices

        :return: list of the monitored devices
        """
        return self._component._devices

    # pylint: enable=protected-access

    def add_device(self, device_name: str) -> None:
        """
        Add device to the monitoring loop

        :param device_name: device name
        :type device_name: str
        """
        if device_name is None:
            return

        if "subarray" in device_name.lower():
            dev_info = SubArrayDeviceInfo(device_name, False)
        elif "dish/master" in device_name.lower():
            dev_info = DishDeviceInfo(device_name, False)
        else:
            dev_info = DeviceInfo(device_name, False)

        self._component.update_device(dev_info)

    def get_device(self, device_name: str) -> DeviceInfo:
        """
        Return the device info our of the monitoring loop with name device_name

        :param device_name: name of the device
        :type device_name: str
        :return: a device info
        :rtype: DeviceInfo
        """
        return self._component.get_device(device_name)

    def update_event_failure(self, device_name: str) -> None:
        """
        Update the failure status of an event for a specific device.
        """
        with self.lock:
            dev_info = self._component.get_device(device_name)
            dev_info.last_event_arrived = time.time()
            dev_info.update_unresponsive(False)

    def update_device_info(self, device_info: DeviceInfo) -> None:
        """
        Update a device with correct monitoring information
        and call the relative callback if available

        :param device_info: a device info
        :type device_info: DeviceInfo
        """
        with self.lock:
            self._component.update_device(device_info)

    def update_exception_for_unresponsiveness(
        self, device_info: DeviceInfo, exception: str
    ) -> None:
        """
        Set a device to failed and call the relative callback if available

        :param device_info: a device info
        :type device_info: DeviceInfo
        :param exception: an exception
        :type: Exception
        """
        with self.lock:
            self._component.update_device_exception(device_info, exception)

    def update_responsiveness_info(self, device_name: str) -> None:
        """
        Update a device with correct responsiveness information.

        :param device_name: name of the device
        :type device_name: str
        """
        with self.lock:
            dev_info: DeviceInfo = self._component.get_device(device_name)
            dev_info.update_unresponsive(False, "")

    def update_device_health_state(
        self, device_name: str, health_state: HealthState
    ) -> None:
        """
        Update a monitored device health state
        aggregate the health states available

        :param device_name: name of the device
        :type device_name: str
        :param health_state: health state of the device
        :type health_state: HealthState
        """
        with self.lock:
            dev_info = self._component.get_device(device_name)
            dev_info.health_state = health_state
            dev_info.last_event_arrived = time.time()
            dev_info.update_unresponsive(False)

    def update_device_state(
        self, device_name: str, state: tango.DevState
    ) -> None:
        """
        Update a monitored device state,
        aggregate the states available
        and call the relative callbacks if available

        :param device_name: name of the device
        :type device_name: str
        :param state: state of the device
        :type state: DevState
        """
        with self.lock:
            dev_info = self._component.get_device(device_name)
            dev_info.state = state
            dev_info.last_event_arrived = time.time()
            dev_info.update_unresponsive(False)

    def is_command_allowed(self, command_name: str):
        """
        Checks whether this command is allowed
        It checks that the device is in a state to perform this command

        :param command_name: command_name
        :type command_name: str

        :rtype: boolean
        :raises NotImplementedError: raise not implemented error
        """
        raise NotImplementedError(
            "is_command_allowed is abstract; method must be implemented in \
            a subclass!"
        )


class TmcLeafNodeComponentManager(BaseTmcComponentManager):
    """
    A component manager for The TMC Leaf Node component.

    It supports:

    * Monitoring its component, e.g. detect that it has been turned off
      or on

    * Fetching the latest SCM indicator values of the components periodically
      and trigger various aggregation logic

    * Receiving the change events from the component
    """

    def __init__(
        self,
        logger: Logger,
        *args,
        _liveliness_probe: LivelinessProbeType = LivelinessProbeType.NONE,
        _event_receiver: bool = False,
        communication_state_callback: Optional[Callable] = None,
        component_state_callback: Optional[Callable] = None,
        proxy_timeout: int = 500,
        event_subscription_check_period: int = 1,
        liveliness_check_period: int = 1,
        **kwargs,
    ):
        """
        Initialise a new ComponentManager instance.

        :param logger: a logger for this component manager
        """
        super().__init__(
            logger,
            _event_receiver,
            communication_state_callback,
            component_state_callback,
            proxy_timeout,
            event_subscription_check_period,
            liveliness_check_period,
            args,
            kwargs,
        )
        self._device = None

    def reset(self) -> None:
        """
        Method for device reset information
        """

    def get_device(self) -> DeviceInfo:
        """
        Return the device info out of the monitoring loop with name device_name
        :return: a device info
        :rtype: DeviceInfo
        """
        return self._device

    def update_device_info(self, device_info: DeviceInfo) -> None:
        """
        Update a device with correct monitoring information
        and call the relative callback if available

        :param device_info: a device info
        :type device_info: DeviceInfo
        """
        with self.lock:
            self._device = device_info

    def update_event_failure(self, device_name: str) -> None:
        """
        Update a monitored device failure status

        :param device_name: name of the device
        :type device_name: str
        """
        with self.lock:
            self._device.last_event_arrived = time.time()
            # self._device.update_unresponsive(False)

    def update_device_health_state(
        self, device_name: str, health_state: HealthState
    ) -> None:
        """
        Update a monitored device health state
        aggregate the health states available

        :param device_name: name of the device
        :type device_name: str
        :param health_state: health state of the device
        :type health_state: HealthState
        """
        with self.lock:
            self._device.health_state = health_state
            self._device.last_event_arrived = time.time()
            # self._device.update_unresponsive(False)

    def update_device_state(
        self, device_name: str, state: tango.DevState
    ) -> None:
        """
        Update a monitored device state,
        aggregate the states available
        and call the relative callbacks if available

        :param device_name: name of the device
        :type device_name: str
        :param state: state of the device
        :type state: DevState
        """
        with self.lock:
            self._device.state = state
            self._device.last_event_arrived = time.time()
            # self._device.update_unresponsive(False)

    def update_device_obs_state(
        self, device_name: str, obs_state: ObsState
    ) -> None:
        """
        Update a monitored device obs state,
        and call the relative callbacks if available

        :param device_name: name of the device
        :type device_name: str
        :param obs_state: obs state of the device
        :type obs_state: ObsState
        """
        with self.lock:
            self._device.obs_state = obs_state
            self._device.last_event_arrived = time.time()
            # self._device.update_unresponsive(False)

    def update_exception_for_unresponsiveness(
        self, device_info: DeviceInfo, exception: str
    ) -> None:
        """
        Set a device to failed and call the relative callback if available

        :param device_info: a device info
        :type device_info: DeviceInfo
        :param exception: an exception
        :type: Exception
        """
        with self.lock:
            device_info.update_unresponsive(True, exception)

    def update_responsiveness_info(self, device_name: str = "") -> None:
        """
        Update a device with correct responsiveness information.

        :param device_name: name of the device
        :type device_name: str
        """
        with self.lock:
            dev_info: DeviceInfo = self.get_device()
            dev_info.update_unresponsive(False, "")
