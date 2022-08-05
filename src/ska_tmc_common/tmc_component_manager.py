"""
This module provided a reference implementation of a BaseComponentManager.

It is provided for explanatory purposes, and to support testing of this
package.
"""
import json
import threading
import time

from ska_tango_base.base import TaskExecutorComponentManager
from ska_tango_base.control_model import HealthState

from ska_tmc_common.device_info import DeviceInfo, SubArrayDeviceInfo
from ska_tmc_common.enum import LivelinessProbeType
from ska_tmc_common.event_receiver import EventReceiver
from ska_tmc_common.liveliness_probe import (
    MultiDeviceLivelinessProbe,
    SingleDeviceLivelinessProbe,
)
from ska_tmc_common.op_state_model import TMCOpStateModel


class TmcComponent:
    def __init__(self, logger):
        self.logger = logger
        # _health_state is never changing. Setter not implemented
        self._health_state = HealthState.OK
        self._devices = []

    def get_device(self, dev_name):
        raise NotImplementedError("This method must be inherited!")

    def update_device(self, dev_info):
        raise NotImplementedError("This method must be inherited!")

    def update_device_exception(self, device_info, exception):
        raise NotImplementedError("This method must be inherited!")

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        raise NotImplementedError("This method must be inherited!")


class BaseTmcComponentManager(TaskExecutorComponentManager):
    def __init__(
        self,
        logger=None,
        _event_receiver=False,
        communication_state_callback=None,
        component_state_callback=None,
        max_workers=5,
        proxy_timeout=500,
        sleep_time=1,
        *args,
        **kwargs,
    ):
        super().__init__(
            logger,
            communication_state_callback,
            component_state_callback,
            max_workers=max_workers,
        )
        self.event_receiver = _event_receiver
        self.max_workers = max_workers
        self.proxy_timeout = proxy_timeout
        self.sleep_time = sleep_time
        self.op_state_model = TMCOpStateModel(logger, callback=None)
        self.lock = threading.Lock()
        self.liveliness_probe_object = None

        if self.event_receiver:
            self.event_receiver_object = EventReceiver(
                self,
                logger=self.logger,
                proxy_timeout=self.proxy_timeout,
                sleep_time=self.sleep_time,
            )

    def is_command_allowed(self, command_name: str):
        """
        Checks whether this command is allowed
        It checks that the device is in a state to perform this command

        :return: True if command is allowed

        :rtype: boolean
        """
        raise NotImplementedError(
            "is_command_allowed is abstract; method must be implemented in a subclass!"
        )

    def start_liveliness_probe(self, lp: LivelinessProbeType) -> None:
        """Starts Liveliness Probe for the given device.

        :param lp: enum of class LivelinessProbeType
        """
        if lp == LivelinessProbeType.SINGLE_DEVICE:
            self.liveliness_probe_object = SingleDeviceLivelinessProbe(
                self,
                logger=self.logger,
                proxy_timeout=self.proxy_timeout,
                sleep_time=self.sleep_time,
            )
            self.liveliness_probe_object.start()

        elif lp == LivelinessProbeType.MULTI_DEVICE:
            self.liveliness_probe_object = MultiDeviceLivelinessProbe(
                self,
                logger=self.logger,
                max_workers=self.max_workers,
                proxy_timeout=self.proxy_timeout,
                sleep_time=self.sleep_time,
            )
            self.liveliness_probe_object.start()
        else:
            self.logger.warning("Liveliness Probe is not running")

    def stop_liveliness_probe(self):
        """Stops the liveliness probe"""
        if self.liveliness_probe_object:
            self.liveliness_probe_object.stop()

    def start_event_receiver(self):
        """Starts the Event Receiver for given device"""
        if self.event_receiver:
            self.event_receiver_object.start()

    def stop_event_receiver(self):
        """Stops the Event Receiver"""
        if self.event_receiver:
            self.event_receiver_object.stop()


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
        _input_parameter,
        logger=None,
        _component=None,
        _liveliness_probe=LivelinessProbeType.MULTI_DEVICE,
        _event_receiver=True,
        communication_state_callback=None,
        component_state_callback=None,
        max_workers=5,
        proxy_timeout=500,
        sleep_time=1,
        *args,
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
            max_workers,
            proxy_timeout,
            sleep_time,
            *args,
            **kwargs,
        )
        self._component = _component or TmcComponent(logger)
        self._devices = []
        self._input_parameter = _input_parameter
        self.start_liveliness_probe(_liveliness_probe)

    def reset(self):
        pass

    @property
    def devices(self):
        """
        Return the list of the monitored devices

        :return: list of the monitored devices
        """
        return self._component._devices

    def add_device(self, dev_name):
        """
        Add device to the monitoring loop

        :param dev_name: device name
        :type dev_name: str
        """
        if dev_name is None:
            return

        if "subarray" in dev_name.lower():
            dev_info = SubArrayDeviceInfo(dev_name, False)
        else:
            dev_info = DeviceInfo(dev_name, False)

        self._component.update_device(dev_info)

    def get_device(self, dev_name):
        """
        Return the device info our of the monitoring loop with name dev_name

        :param dev_name: name of the device
        :type dev_name: str
        :return: a device info
        :rtype: DeviceInfo
        """
        return self._component.get_device(dev_name)

    def device_failed(self, device_info, exception):
        """
        Set a device to failed and call the relative callback if available

        :param device_info: a device info
        :type device_info: DeviceInfo
        :param exception: an exception
        :type: Exception
        """
        with self.lock:
            self._component.update_device_exception(device_info, exception)

    def update_event_failure(self, dev_name):
        with self.lock:
            dev_info = self._component.get_device(dev_name)
            dev_info.last_event_arrived = time.time()
            dev_info.update_unresponsive(False)

    def update_device_info(self, device_info):
        """
        Update a device with correct monitoring information
        and call the relative callback if available

        :param device_info: a device info
        :type device_info: DeviceInfo
        """
        with self.lock:
            self._component.update_device(device_info)

    def update_ping_info(self, ping, dev_name):
        """
        Update a device with correct ping information.

        :param dev_name: name of the device
        :type dev_name: str
        :param ping: device response time
        :type ping: int
        """
        with self.lock:
            dev_info = self._component.get_device(dev_name)
            dev_info.ping = ping

    def update_device_health_state(self, dev_name, health_state):
        """
        Update a monitored device health state
        aggregate the health states available

        :param dev_name: name of the device
        :type dev_name: str
        :param health_state: health state of the device
        :type health_state: HealthState
        """
        with self.lock:
            dev_info = self.component.get_device(dev_name)
            dev_info.health_state = health_state
            dev_info.last_event_arrived = time.time()
            dev_info.update_unresponsive(False)

    def update_device_state(self, dev_name, state):
        """
        Update a monitored device state,
        aggregate the states available
        and call the relative callbacks if available

        :param dev_name: name of the device
        :type dev_name: str
        :param state: state of the device
        :type state: DevState
        """
        with self.lock:
            dev_info = self._component.get_device(dev_name)
            dev_info.state = state
            dev_info.last_event_arrived = time.time()
            dev_info.update_unresponsive(False)


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
        logger=None,
        _liveliness_probe=LivelinessProbeType.NONE,
        _event_receiver=False,
        communication_state_callback=None,
        component_state_callback=None,
        max_workers=5,
        proxy_timeout=500,
        sleep_time=1,
        *args,
        **kwargs,
    ):
        """
        Initialise a new ComponentManager instance.

        :param logger: a logger for this component manager
        """
        super().__init__(
            logger,
            _liveliness_probe,
            _event_receiver,
            communication_state_callback,
            component_state_callback,
            max_workers,
            proxy_timeout,
            sleep_time,
            args,
            kwargs,
        )
        self._device = None  # It should be an object of DeviceInfo class
        self.start_liveliness_probe(_liveliness_probe)
        self.start_event_receiver()

    def reset(self):
        pass

    def get_device(self):
        """
        Return the device info our of the monitoring loop with name dev_name

        :param None:
        :return: a device info
        :rtype: DeviceInfo
        """
        return self._device

    def device_failed(self, exception):
        """
        Set a device to failed and call the relative callback if available

        :param exception: an exception
        :type: Exception
        """
        with self.lock:
            self._device.exception = exception

    def update_device_info(self, device_info):
        """
        Update a device with correct monitoring information
        and call the relative callback if available

        :param device_info: a device info
        :type device_info: DeviceInfo
        """
        with self.lock:
            self._device = device_info

    def update_ping_info(self, ping: int, dev_name: str) -> None:
        """
        Update a device with the correct ping information.

        :param dev_name: name of the device
        :type dev_name: str
        :param ping: device response time
        :type ping: int
        """
        with self.lock:
            self._device.ping = ping

    def update_event_failure(self):
        with self.lock:
            self._device.last_event_arrived = time.time()
            self._device.update_unresponsive(False)

    def update_device_health_state(self, health_state):
        """
        Update a monitored device health state
        aggregate the health states available

        :param health_state: health state of the device
        :type health_state: HealthState
        """
        with self.lock:
            self._device.health_state = health_state
            self._device.last_event_arrived = time.time()
            self._device.update_unresponsive(False)

    def update_device_state(self, state):
        """
        Update a monitored device state,
        aggregate the states available
        and call the relative callbacks if available

        :param state: state of the device
        :type state: DevState
        """
        with self.lock:
            self._device.state = state
            self._device.last_event_arrived = time.time()
            self._device.update_unresponsive(False)

    def update_device_obs_state(self, obs_state):
        """
        Update a monitored device obs state,
        and call the relative callbacks if available

        :param obs_state: obs state of the device
        :type obs_state: ObsState
        """
        with self.lock:
            self._device.obs_state = obs_state
            self._device.last_event_arrived = time.time()
            self._device.update_unresponsive(False)
