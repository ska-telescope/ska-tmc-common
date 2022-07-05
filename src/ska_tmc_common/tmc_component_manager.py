"""
This module provided a reference implementation of a BaseComponentManager.

It is provided for explanatory purposes, and to support testing of this
package.
"""
import json
import threading
import time

from ska_tango_base.base import (
    BaseComponentManager,
    TaskExecutorComponentManager,
)
from ska_tango_base.control_model import HealthState

from ska_tmc_common.device_info import DeviceInfo, SubArrayDeviceInfo
from ska_tmc_common.event_receiver import EventReceiver
from ska_tmc_common.monitoring_loop import MonitoringLoop
from ska_tmc_common.op_state_model import TMCOpStateModel


class TmcComponent:
    def __init__(self, logger):
        self.logger = logger
        # _health_state is never changing. Setter not implemented
        self._health_state = HealthState.OK
        self._devices = []

    def get_device(self, dev_name):
        raise NotImplementedError("This class must be inherited!")

    def update_device(self, dev_info):
        raise NotImplementedError("This class must be inherited!")

    def update_device_exception(self, device_info, exception):
        raise NotImplementedError("This class must be inherited!")

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        raise NotImplementedError("This class must be inherited!")


class TmcComponentManager(TaskExecutorComponentManager):
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
        _component=None,
        logger=None,
        _monitoring_loop=True,
        _event_receiver=True,
        communication_state_changed_callback=None,
        component_state_changed_callback=None,
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
        self.logger = logger
        self.lock = threading.Lock()
        self.component = _component or TmcComponent(logger)
        self.op_state_model = TMCOpStateModel
        self.devices = []

        self._monitoring_loop = None
        if _monitoring_loop:
            self._monitoring_loop = MonitoringLoop(
                self,
                logger,
                max_workers=max_workers,
                proxy_timeout=proxy_timeout,
                sleep_time=sleep_time,
            )

        self._event_receiver = None
        if _event_receiver:
            self._event_receiver = EventReceiver(
                self,
                logger,
                proxy_timeout=proxy_timeout,
                sleep_time=sleep_time,
            )

        super().__init__(
            max_workers,
            communication_state_changed_callback,
            component_state_changed_callback,
        )

    def reset(self):
        pass

    def stop(self):
        self._monitoring_loop.stop()
        self._event_receiver.stop()

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

        self.component.update_device(dev_info)

    def get_device(self, dev_name):
        """
        Return the device info our of the monitoring loop with name dev_name

        :param dev_name: name of the device
        :type dev_name: str
        :return: a device info
        :rtype: DeviceInfo
        """
        return self.component.get_device(dev_name)

    def device_failed(self, device_info, exception):
        """
        Set a device to failed and call the relative callback if available

        :param device_info: a device info
        :type device_info: DeviceInfo
        :param exception: an exception
        :type: Exception
        """
        with self.lock:
            self.component.update_device_exception(device_info, exception)

    def update_event_failure(self, dev_name):
        with self.lock:
            dev_info = self.component.get_device(dev_name)
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
            self.component.update_device(device_info)

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
            dev_info = self.component.get_device(dev_name)
            dev_info.state = state
            dev_info.last_event_arrived = time.time()
            dev_info.update_unresponsive(False)

    def telescope_on(self, task_callback=None):
        """
        Turn on the Telescope.

        :param task_callback: Update task state, defaults to None

        :return: a TaskStatus and message
        """
        raise NotImplementedError(
            "TmcComponentManager is abstract; method telescope_on must be implemented in a subclass!"
        )

    def telescope_off(self, task_callback=None):
        """
        Turn off the Telescope.

        :param task_callback: Update task state, defaults to None

        :return: a TaskStatus and message
        """
        raise NotImplementedError(
            "TmcComponentManager is abstract; method telescope_off must be implemented in a subclass!"
        )

    def telescope_standby(self, task_callback=None):
        """
        Turn off the Telescope.

        :param task_callback: Update task state, defaults to None

        :return: a TaskStatus and message
        """
        raise NotImplementedError(
            "TmcComponentManager is abstract; method telescope_standby must be implemented in a subclass!"
        )

    def assign_resources(self, task_callback=None):
        """
        Turn off the Telescope.

        :param task_callback: Update task state, defaults to None

        :return: a TaskStatus and message
        """
        raise NotImplementedError(
            "TmcComponentManager is abstract; method assign_resources must be implemented in a subclass!"
        )

    def release_resources(self, task_callback=None):
        """
        Turn off the Telescope.

        :param task_callback: Update task state, defaults to None

        :return: a TaskStatus and message
        """
        raise NotImplementedError(
            "TmcComponentManager is abstract; method release_resources must be implemented in a subclass!"
        )

    def check_if_command_is_allowed(self):
        """
        Checks whether this command is allowed
        It checks that the device is in a state
        to perform this command

        :return: True if command is allowed

        :rtype: boolean
        """
        raise NotImplementedError(
            "TmcComponentManager is abstract; method check_if_command_is_allowed must be implemented in a subclass!"
        )


class TmcLeafNodeComponentManager(BaseComponentManager):
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
        op_state_model,
        logger=None,
        _monitoring_loop=False,
        _event_receiver=False,
        max_workers=5,
        proxy_timeout=500,
        sleep_time=1,
        *args,
        **kwargs,
    ):
        """
        Initialise a new ComponentManager instance.

        :param op_state_model: the op state model used by this component
            manager
        :param logger: a logger for this component manager
        :param _component: allows setting of the component to be
            managed; for testing purposes only
        """
        self.logger = logger
        self.lock = threading.Lock()
        self._device = None  # It should be an object of DeviceInfo class

        self._monitoring_loop = None
        if _monitoring_loop:
            self._monitoring_loop = MonitoringLoop(
                self,
                logger,
                max_workers=max_workers,
                proxy_timeout=proxy_timeout,
                sleep_time=sleep_time,
            )

        self._event_receiver = None
        if _event_receiver:
            self._event_receiver = EventReceiver(
                self,
                logger,
                proxy_timeout=proxy_timeout,
                sleep_time=sleep_time,
            )

        super().__init__(op_state_model, *args, **kwargs)

    def reset(self):
        pass

    def stop(self):
        if self._event_receiver:
            self._event_receiver.stop()
        if self._monitoring_loop:
            self._monitoring_loop.stop()

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
