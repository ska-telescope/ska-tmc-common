import logging
import time

import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import HealthState
from ska_tango_base.executor import TaskStatus

from ska_tmc_common import TimeKeeper, TimeoutCallback, TimeoutState
from tests.settings import DummyComponentManager, State

logger = logging.getLogger(__name__)


def test_timer_thread():
    cm = DummyComponentManager(logger)
    timer_id = f"{time.time()}-{cm.__class__.__name__}"
    timeout_callback = TimeoutCallback(timer_id, logger)
    cm.start_timer(timer_id, 10, timeout_callback)
    assert cm.timer_object.is_alive()
    cm.stop_timer()
    time.sleep(0.5)
    assert not cm.timer_object.is_alive()


def test_timekeeper_class():
    timekeeper = TimeKeeper(10, logger)
    timer_id = f"{time.time()}-{TimeKeeper.__name__}"
    timeout_callback = TimeoutCallback(timer_id, logger)
    timekeeper.start_timer(timer_id, timeout_callback)
    assert timekeeper.timer_object.is_alive()
    timekeeper.stop_timer()
    time.sleep(0.5)
    assert not timekeeper.timer_object.is_alive()

    timekeeper.time_out = 1
    timekeeper.start_timer(timer_id, timeout_callback)
    assert timekeeper.timer_object.is_alive()
    time.sleep(1.5)
    assert timeout_callback.assert_against_call(timer_id, TimeoutState.OCCURED)


def test_timeout_callback():
    timer_id = f"{time.time()}-{__name__}"
    timeout_callback = TimeoutCallback(timer_id, logger)
    assert timeout_callback.assert_against_call(
        timer_id, TimeoutState.NOT_OCCURED
    )
    timeout_callback(timer_id, TimeoutState.OCCURED)
    assert timeout_callback.assert_against_call(timer_id, TimeoutState.OCCURED)
    assert not timeout_callback.assert_against_call(
        "123", TimeoutState.OCCURED
    )
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
    assert not timeout_callback.assert_against_call(
        timer_id,
        TimeoutState.OCCURED,
        state=HealthState.DEGRADED,
        abc="String",
        kwarg2=24,
        kwarg3=12.6,
    )


def test_command_timeout_success(task_callback):
    cm = DummyComponentManager(logger)
    cm.invoke_command(True, task_callback)
    task_callback.assert_against_call(status=TaskStatus.QUEUED)
    cm.command_obj.state = State.CHANGED
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED, result=ResultCode.OK
    )
    time.sleep(0.5)
    assert not cm.timer_object.is_alive()


def test_command_timeout_failure(task_callback):
    cm = DummyComponentManager(logger)
    cm.timeout = 2
    cm.invoke_command(True, task_callback)
    time.sleep(3)
    task_callback.assert_against_call(status=TaskStatus.QUEUED)
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED,
        result=ResultCode.FAILED,
        exception="Timeout has occurred, command failed",
    )
