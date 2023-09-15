"""
This module contains the fixtures, methods and variables required for testing.
"""

import logging
import threading
import time
from enum import IntEnum, unique
from logging import Logger
from typing import Any, Callable, Optional, Tuple

import tango
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus

from ska_tmc_common import (
    DevFactory,
    DeviceInfo,
    DishDeviceInfo,
    FaultType,
    InputParameter,
    LivelinessProbeType,
    LRCRCallback,
    SubArrayDeviceInfo,
    TimeoutCallback,
    TmcComponentManager,
    TmcLeafNodeCommand,
    TmcLeafNodeComponentManager,
)

logger = logging.getLogger(__name__)

SLEEP_TIME = 0.5
TIMEOUT = 10

DishLeafNodePrefix = "ska_mid/tm_leaf_node/d0"
NumDishes = 10

DEVICE_LIST = ["dummy/tmc/device", "test/device/1", "test/device/2"]
SUBARRAY_DEVICE = "helper/subarray/device"
SDP_SUBARRAY_DEVICE = "helper/sdpsubarray/device"
CSP_SUBARRAY_DEVICE = "helper/cspsubarray/device"
SUBARRAY_LEAF_DEVICE = "helper/subarrayleaf/device"
DISH_DEVICE = "helper/dish/device"
CSP_DEVICE = "helper/csp/device"
CSP_LEAF_NODE_DEVICE = "helper/cspsubarrayleafnode/device"
SDP_LEAF_NODE_DEVICE = "helper/sdpsubarrayleafnode/device"
HELPER_SUBARRAY_DEVICE = "test/subarray/1"
HELPER_SDP_SUBARRAY_DEVICE = "test/sdpsubarray/1"
HELPER_CSP_SUBARRAY_DEVICE = "test/cspsubarray/1"
HELPER_MCCS_STATE_DEVICE = "test/mccs/1"
HELPER_BASE_DEVICE = "test/base/1"
HELPER_DISH_DEVICE = "test/dish/1"
HELPER_CSP_MASTER_DEVICE = "test/csp_master/1"
DISH_FQDN = "ska_mid/tm_leaf_node/d0001"
TMC_COMMON_DEVICE = "src/tmc/common"

FAILED_RESULT_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.FAILED_RESULT,
    "error_message": "Device is defective, cannot process command completely.",
    "result": ResultCode.FAILED,
}

COMMAND_NOT_ALLOWED_DEFECT = {
    "enabled": True,
    "fault_type": FaultType.COMMAND_NOT_ALLOWED,
    "error_message": "Device is stuck in Resourcing state",
    "result": ResultCode.FAILED,
}


@unique
class State(IntEnum):
    """Integer enum for testing"""

    NORMAL = 1
    CHANGED = 2
    TRANSITIONAL = 3


def count_faulty_devices(cm):
    """
    It counts the number of faulty devices present.
    """
    result = 0
    for dev_info in cm.checked_devices:
        if dev_info.unresponsive:
            result += 1
    return result


def create_cm(
    _input_parameter: InputParameter = InputParameter(None),
    p_liveliness_probe: LivelinessProbeType = LivelinessProbeType.MULTI_DEVICE,
    p_event_receiver: bool = True,
) -> Tuple[TmcComponentManager, float]:
    """
    It creates the instance of the component manager class.
    """
    cm = TmcComponentManager(
        _input_parameter=_input_parameter,
        logger=logger,
        _liveliness_probe=p_liveliness_probe,
        _event_receiver=p_event_receiver,
    )

    start_time = time.time()
    return cm, start_time


class DummyComponentManager(TmcLeafNodeComponentManager):
    """Dummy CM for testing"""

    def __init__(
        self,
        logger: Logger,
        *args,
        _liveliness_probe: LivelinessProbeType = LivelinessProbeType.NONE,
        _event_receiver: bool = False,
        transitional_obsstate: bool = False,
        communication_state_callback: Callable[..., Any] | None = None,
        component_state_callback: Callable[..., Any] | None = None,
        max_workers: int = 5,
        proxy_timeout: int = 500,
        sleep_time: int = 1,
        **kwargs,
    ):
        super().__init__(
            logger,
            _liveliness_probe,
            _event_receiver,
            communication_state_callback,
            component_state_callback,
            max_workers,
            proxy_timeout,
            sleep_time,
            *args,
            **kwargs,
        )
        self.device_info: DeviceInfo
        self.command_id: Optional[str] = None
        self.timeout = 10
        self.lrcr_callback = LRCRCallback(self.logger)
        self.transitional_obsstate = transitional_obsstate
        self.command_obj = DummyCommandClass(self, self.logger)

    def add_device(self, dev_name: str) -> None:
        """
        Add device to the monitoring loop

        :param dev_name: device name
        :type dev_name: str
        """
        if dev_name is None:
            return

        if "subarray" in dev_name.lower():
            self.device_info = SubArrayDeviceInfo(dev_name, False)
        elif "dish/master" in dev_name.lower():
            self.device_info = DishDeviceInfo(dev_name, False)
        else:
            self.device_info = DeviceInfo(dev_name, False)

    def invoke_command(
        self, argin, task_callback: Callable
    ) -> Tuple[TaskStatus, str]:
        """Submits the command for execution."""
        self.command_id = f"{time.time()}-{DummyCommandClass.__name__}"
        self.logger.info(
            "Submitting the command in Queue. Command ID is %s",
            self.command_id,
        )
        status, msg = self.submit_task(
            self.command_obj.invoke_do,
            args=[argin, self.timeout],
            task_callback=task_callback,
        )
        return status, msg


class DummyCommandClass(TmcLeafNodeCommand):
    """Dummy Command class for testing"""

    def __init__(
        self,
        component_manager: DummyComponentManager,
        logger: Logger,
        *args,
        **kwargs,
    ):
        super().__init__(component_manager, logger, *args, **kwargs)
        self._timeout_id = f"{time.time()}-{self.__class__.__name__}"
        self.timeout_callback = TimeoutCallback(self._timeout_id, self.logger)
        self._state_val = State.NORMAL
        self.task_callback: Callable
        self.transitional_obsstate = component_manager.transitional_obsstate

    @property
    def state(self) -> IntEnum:
        """Return the State value"""
        return self._state_val

    @state.setter
    def state(self, value: IntEnum) -> None:
        """Sets the State Value"""
        self._state_val = value

    def get_state(self) -> IntEnum:
        """Method to get the state value."""
        return self.state

    def invoke_do(
        self,
        argin: bool,
        timeout: int,
        task_callback: Callable,
        task_abort_event: threading.Event,
    ) -> None:
        """Invokes the do method and updates the task status."""
        self.logger.info("Starting timer for timeout")
        if self._timeout_id:
            self.component_manager.start_timer(
                self._timeout_id, timeout, self.timeout_callback
            )
        self.task_callback = task_callback
        self.logger.info("Invoking do with argin: %s", argin)
        result, msg = self.do(argin)
        if result == ResultCode.OK:
            self.logger.info("Starting tracker for timeout and exceptions.")
            if self.transitional_obsstate:
                self.start_tracker_thread(
                    self.get_state,
                    [State.TRANSITIONAL, State.CHANGED],
                    task_abort_event,
                    self._timeout_id,
                    self.timeout_callback,
                    self.component_manager.command_id,
                    self.component_manager.lrcr_callback,
                )
            else:
                self.start_tracker_thread(
                    self.get_state,
                    [State.CHANGED],
                    task_abort_event,
                    self._timeout_id,
                    self.timeout_callback,
                    self.component_manager.command_id,
                    self.component_manager.lrcr_callback,
                )
        else:
            self.logger.error("Command Failed")
            if self._timeout_id:
                self.component_manager.stop_timer()
            self.update_task_status(result=result, msg=msg)

    # pylint: disable=signature-differs
    def do(self, argin: bool) -> Tuple[ResultCode, str]:
        """Do method for command class."""
        time.sleep(2)
        if argin:
            return ResultCode.OK, ""
        return ResultCode.FAILED, ""

    def update_task_status(
        self,
        **kwargs,
    ) -> None:
        """Method to update the task status."""
        result = kwargs.get("result")
        status = kwargs.get("status", TaskStatus.COMPLETED)
        message = kwargs.get("message")

        if result == ResultCode.OK:
            self.task_callback(result=result, status=status)
        else:
            self.task_callback(
                result=result,
                status=status,
                exception=message,
            )


def set_devices_state(
    devices: list, state: tango.DevState, devFactory: DevFactory
) -> None:
    """
    It sets the state of multiple devices
    """
    for device in devices:
        proxy = devFactory.get_device(device)
        proxy.SetDirectState(state)
        assert proxy.State() == state


def set_device_state(
    device: str, state: tango.DevState, devFactory: DevFactory
) -> None:
    """
    It sets the state of the device
    """
    proxy = devFactory.get_device(device)
    proxy.SetDirectState(state)
    assert proxy.State() == state


def wait_for_obstate(device: tango.DeviceProxy, expected_obsstate: ObsState):
    """
    Waits for Device ObsState to transition to Expected ObsState.
    Raises an Exception in case of failure."""
    device_obsstate = device.read_attribute("obsState").value
    start_time = time.time()
    elapsed_time = 0
    logger.info("Current %s ObsState is : %s", device, device_obsstate)
    while device_obsstate != expected_obsstate:
        device_obsstate = device.read_attribute("obsState").value
        elapsed_time = time.time() - start_time
        if elapsed_time > TIMEOUT:
            logger.exception(
                "Timeout occured while waiting for %s ObsState to transition\
                    to %s",
                device,
                expected_obsstate,
            )
            raise Exception(
                f"Timeout occured while waiting for {device} ObsState to \
                    transition to {expected_obsstate}"
            )
    logger.info("ObsState of %s transitioned to %s", device, expected_obsstate)
    assert device.read_attribute("obsState").value == expected_obsstate
