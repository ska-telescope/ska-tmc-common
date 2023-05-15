import logging
import time

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import HealthState
from ska_tango_base.executor import TaskStatus

from ska_tmc_common import LRCRCallback
from tests.settings import DummyComponentManager

logger = logging.getLogger(__name__)


def test_lrcr_callback():
    command_id = f"{time.time()}-{__name__}"
    lrcr_callback = LRCRCallback(logger)
    lrcr_callback(command_id, ResultCode.STARTED)
    assert lrcr_callback.assert_against_call(command_id, ResultCode.STARTED)
    assert not lrcr_callback.assert_against_call(command_id, ResultCode.OK)
    assert not lrcr_callback.assert_against_call(command_id, ResultCode.FAILED)
    assert not lrcr_callback.assert_against_call("123", ResultCode.STARTED)


def test_kwargs_functionality_lrcr_callback():
    command_id = f"{time.time()}-{__name__}"
    lrcr_callback = LRCRCallback(logger)
    lrcr_callback(command_id, ResultCode.FAILED, state=HealthState.OK)
    assert lrcr_callback.assert_against_call(
        command_id, ResultCode.FAILED, state=HealthState.OK
    )

    lrcr_callback(
        command_id,
        ResultCode.FAILED,
        state=HealthState.DEGRADED,
    )
    assert lrcr_callback.assert_against_call(command_id, ResultCode.FAILED)
    assert lrcr_callback.assert_against_call(
        command_id,
        ResultCode.FAILED,
        state=HealthState.DEGRADED,
    )

    lrcr_callback(command_id, ResultCode.OK)
    assert not lrcr_callback.assert_against_call(
        command_id,
        ResultCode.OK,
        state=HealthState.OK,
    )

    lrcr_callback(
        command_id,
        ResultCode.FAILED,
        kwarg1="String",
        kwarg2=24,
        kwarg3=12.6,
    )
    assert lrcr_callback.assert_against_call(
        command_id,
        ResultCode.FAILED,
        state=HealthState.DEGRADED,
        kwarg1="String",
        kwarg2=24,
        kwarg3=12.6,
    )
    assert not lrcr_callback.assert_against_call(
        command_id,
        ResultCode.FAILED,
        state=HealthState.DEGRADED,
        abc="String",
        kwarg2=24,
        kwarg3=12.6,
    )


def test_command_propogation_success(task_callback, caplog):
    cm = DummyComponentManager(logger)
    cm.invoke_command(True, task_callback)
    cm.lrcr_callback(
        cm.command_id,
        ResultCode.FAILED,
        exception_msg="Exception has occured",
    )
    time.sleep(2)
    caplog.set_level(logging.DEBUG, logger="ska-tango-testing.mock")
    task_callback.assert_against_call(
        status=TaskStatus.QUEUED,
    )
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED,
        result=ResultCode.FAILED,
        exception="Exception has occured",
    )
