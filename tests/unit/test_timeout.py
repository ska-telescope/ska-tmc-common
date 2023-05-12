import logging
import time
from enum import IntEnum, unique
from logging import Logger
from typing import Callable, Tuple

import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import HealthState
from ska_tango_base.executor import TaskStatus

from ska_tmc_common import (
    TimeoutCallback,
    TimeoutState,
    TmcLeafNodeCommand,
    TmcLeafNodeComponentManager,
)

logger = logging.getLogger(__name__)


@unique
class State(IntEnum):
    """Integer enum for testing"""

    NORMAL = 1
    CHANGED = 2


class DummyCommandClass(TmcLeafNodeCommand):
    """Dummy Command class for testing"""

    def __init__(self, component_manager, logger: Logger, *args, **kwargs):
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
        self, argin: bool, timeout: int, task_callback: Callable
    ) -> None:
        self.component_manager.start_timer(
            self._timeout_id, timeout, self.timeout_callback
        )
        self.task_callback = task_callback
        result, _ = self.do(argin)
        if result == ResultCode.OK:
            self.start_tracker_thread(
                self.get_state,
                State.CHANGED,
                self._timeout_id,
                self.timeout_callback,
            )
        else:
            self.logger.error("Command Failed")

    def do(self, argin: bool) -> Tuple[ResultCode, str]:
        time.sleep(2)
        if argin:
            return ResultCode.OK, ""
        else:
            return ResultCode.FAILED, ""

    def update_task_status(
        self, result: ResultCode, message: str = ""
    ) -> None:
        self.component_manager.stop_timer()
        if result == ResultCode.OK:
            self.task_callback(result=result, status=TaskStatus.COMPLETED)
        else:
            self.task_callback(
                result=result,
                status=TaskStatus.COMPLETED,
                exception=message,
            )


def test_timer_thread():
    cm = TmcLeafNodeComponentManager(logger)
    timer_id = f"{time.time()}-{cm.__class__.__name__}"
    timeout_callback = TimeoutCallback(timer_id, logger)
    cm.start_timer(timer_id, 10, timeout_callback)
    assert cm.timer_object.is_alive()
    cm.stop_timer()
    time.sleep(0.5)
    assert not cm.timer_object.is_alive()


def test_timeout_callback():
    timer_id = f"{time.time()}-{__name__}"
    timeout_callback = TimeoutCallback(timer_id, logger)
    assert timeout_callback.assert_against_call(
        timer_id, TimeoutState.NOT_OCCURED
    )
    timeout_callback(timer_id, TimeoutState.OCCURED)
    assert timeout_callback.assert_against_call(timer_id, TimeoutState.OCCURED)
    with pytest.raises(ValueError):
        timeout_callback("123", TimeoutState.OCCURED)


def test_kwargs_functionality_timeout_callback():
    timer_id = f"{time.time()}-{__name__}"
    timeout_callback = TimeoutCallback(timer_id, logger)
    timeout_callback(timer_id, TimeoutState.OCCURED, state=HealthState.OK)
    assert timeout_callback.assert_against_call(
        timer_id, TimeoutState.OCCURED, state=HealthState.OK
    )

    timeout_callback(
        timer_id, TimeoutState.OCCURED, state=HealthState.DEGRADED
    )
    assert timeout_callback.assert_against_call(timer_id, TimeoutState.OCCURED)

    timeout_callback(timer_id, TimeoutState.OCCURED)
    assert not timeout_callback.assert_against_call(
        timer_id,
        TimeoutState.OCCURED,
        state=HealthState.OK,
    )

    timeout_callback(
        timer_id, TimeoutState.OCCURED, kwarg1="String", kwarg2=24, kwarg3=12.6
    )
    assert timeout_callback.assert_against_call(
        timer_id,
        TimeoutState.OCCURED,
        state=HealthState.DEGRADED,
        kwarg1="String",
        kwarg2=24,
        kwarg3=12.6,
    )


def test_command_timeout_success(task_callback):
    cm = TmcLeafNodeComponentManager(logger)
    dummy_command = DummyCommandClass(cm, logger)
    dummy_command.invoke_do(True, 10, task_callback)
    dummy_command.state = State.CHANGED
    time.sleep(2)
    assert not cm.timer_object.is_alive()
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED, result=ResultCode.OK
    )


def test_command_timeout_failure(task_callback):
    cm = TmcLeafNodeComponentManager(logger)
    dummy_command = DummyCommandClass(cm, logger)
    dummy_command.invoke_do(True, 2, task_callback)
    time.sleep(3)
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED,
        result=ResultCode.FAILED,
        exception="Timeout has occured, command failed",
    )
