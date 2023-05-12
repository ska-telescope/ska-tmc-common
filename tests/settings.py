import logging
import threading
import time
from enum import IntEnum, unique
from logging import Logger
from typing import Any, Callable, Optional, Tuple

import pytest
import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus

from ska_tmc_common import (
    DevFactory,
    DeviceInfo,
    DishDeviceInfo,
    DummyTmcDevice,
    HelperBaseDevice,
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


@unique
class State(IntEnum):
    """Integer enum for testing"""

    NORMAL = 1
    CHANGED = 2


@pytest.fixture(scope="module")
def devices_to_load():
    return (
        {
            "class": DummyTmcDevice,
            "devices": [{"name": "dummy/tmc/device"}],
        },
        {
            "class": HelperBaseDevice,
            "devices": [{"name": "test/device/1"}, {"name": "test/device/2"}],
        },
    )


def count_faulty_devices(cm):
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
        _liveliness_probe: LivelinessProbeType = LivelinessProbeType.NONE,
        _event_receiver: bool = False,
        communication_state_callback: Callable[..., Any] | None = None,
        component_state_callback: Callable[..., Any] | None = None,
        max_workers: int = 5,
        proxy_timeout: int = 500,
        sleep_time: int = 1,
        *args,
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

    @property
    def state(self) -> IntEnum:
        return self._state_val

    @state.setter
    def state(self, value: IntEnum) -> None:
        self._state_val = value

    def get_state(self) -> IntEnum:
        return self.state

    def invoke_do(
        self,
        argin: bool,
        timeout: int,
        task_callback: Callable,
        task_abort_event: Optional[threading.Event] = None,
    ) -> None:
        self.logger.info("Starting timer for timeout")
        self.component_manager.start_timer(
            self._timeout_id, timeout, self.timeout_callback
        )
        self.task_callback = task_callback
        self.logger.info("Invoking do with argin: %s", argin)
        result, msg = self.do(argin)
        if result == ResultCode.OK:
            self.logger.info("Starting tracker for timeout and exceptions.")
            self.start_tracker_thread(
                self.get_state,
                State.CHANGED,
                self._timeout_id,
                self.timeout_callback,
                self.component_manager.command_id,
                self.component_manager.lrcr_callback,
            )
        else:
            self.logger.error("Command Failed")
            self.update_task_status(result, msg)

    def do(self, argin: bool) -> Tuple[ResultCode, str]:
        time.sleep(2)
        if argin:
            return ResultCode.OK, ""
        else:
            return ResultCode.FAILED, ""

    def update_task_status(
        self, result: ResultCode, message: str = ""
    ) -> None:
        if result == ResultCode.OK:
            self.task_callback(result=result, status=TaskStatus.COMPLETED)
        else:
            self.task_callback(
                result=result,
                status=TaskStatus.COMPLETED,
                exception=message,
            )


def set_devices_state(
    devices: list, state: tango.DevState, devFactory: DevFactory
) -> None:
    for device in devices:
        proxy = devFactory.get_device(device)
        proxy.SetDirectState(state)
        assert proxy.State() == state


def set_device_state(
    device: str, state: tango.DevState, devFactory: DevFactory
) -> None:
    proxy = devFactory.get_device(device)
    proxy.SetDirectState(state)
    assert proxy.State() == state
