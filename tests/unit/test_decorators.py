"""A module to test the timeout and error propagation decorators"""
import time
from enum import IntEnum
from logging import Logger
from typing import Callable, Optional, Tuple

from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskExecutorComponentManager, TaskStatus

from ska_tmc_common import (
    DeviceInfo,
    LRCRCallback,
    TimeKeeper,
    TimeoutCallback,
    TmcLeafNodeCommand,
    error_propagation_decorator,
    timeout_decorator,
)
from tests.settings import State, logger


class DummyComponentManager(TaskExecutorComponentManager):
    """Dummy CM for testing"""

    def __init__(
        self,
        dev_name: str,
        logger: Logger,
        timeout: int = 10,
        transitional_obsstate: bool = False,
    ):
        super().__init__(logger=logger)
        self.logger = logger
        self.device_info: DeviceInfo = DeviceInfo(dev_name)
        self.command_id: Optional[str] = None
        self.timeout = timeout
        self.timekeeper = TimeKeeper(self.timeout, self.logger)
        self.long_running_result_callback = LRCRCallback(self.logger)
        self.transitional_obsstate = transitional_obsstate
        self.command_obj = DummyCommandClass(
            self, self.timekeeper, self.logger
        )
        self._state_val = State.NORMAL

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
            self.command_obj.do,
            args=[argin, self.timeout],
            task_callback=task_callback,
        )
        return status, msg

    def invoke_command_without_input(
        self, task_callback: Callable
    ) -> Tuple[TaskStatus, str]:
        """Submits the command for execution."""
        self.command_id = f"{time.time()}-{DummyCommandClass.__name__}"
        self.logger.info(
            "Submitting the command in Queue. Command ID is %s",
            self.command_id,
        )
        status, msg = self.submit_task(
            self.command_obj.do_without_input,
            args=[self.timeout],
            task_callback=task_callback,
        )
        return status, msg


class DummyCommandClass(TmcLeafNodeCommand):
    """Dummy Command class for testing"""

    def __init__(
        self,
        component_manager: DummyComponentManager,
        timekeeper: TimeKeeper,
        logger: Logger,
    ):
        super().__init__(component_manager, logger)
        self.timekeeper = timekeeper
        self.timeout_id = f"{time.time()}-{self.__class__.__name__}"
        self.timeout_callback = TimeoutCallback(self.timeout_id, self.logger)
        self.task_callback: Callable
        self.transitional_obsstate = component_manager.transitional_obsstate

    def clear_state(self):
        """Cleanup method"""
        self.component_manager.state = State.NORMAL

    @error_propagation_decorator(
        "get_state", [State.CHANGED], cleanup_function="clear_state"
    )
    @timeout_decorator
    def do(self, argin: str) -> Tuple[ResultCode, str]:
        """Do method for command class."""
        time.sleep(1)
        if argin:
            return ResultCode.OK, ""
        return ResultCode.FAILED, ""

    @error_propagation_decorator(
        "get_state", [State.CHANGED], cleanup_function="clear_state"
    )
    @timeout_decorator
    def do_without_input(self) -> Tuple[ResultCode, str]:
        """Do method for command class."""
        time.sleep(1)
        return ResultCode.OK, ""

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


def test_timeout(task_callback):
    """Test the timeout decorator."""
    cm = DummyComponentManager("test/device/1", logger, 2)
    cm.invoke_command("True", task_callback)
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED,
        result=ResultCode.FAILED,
        exception="Timeout has occurred, command failed",
        lookahead=3,
    )


def test_error_propagation_failed_result(task_callback):
    """Test error propagation decorator's result handling"""
    cm = DummyComponentManager("test/device/1", logger)
    cm.invoke_command("", task_callback)
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED,
        result=ResultCode.FAILED,
        exception="",
        lookahead=3,
    )


def test_error_propagation_no_input(task_callback):
    """Test error propagation decorator's result handling"""
    cm = DummyComponentManager("test/device/1", logger)
    cm.invoke_command_without_input(task_callback)
    cm.state = State.CHANGED
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED,
        result=ResultCode.OK,
        lookahead=3,
    )
