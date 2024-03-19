import time

import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus
from tango import DevFailed

from ska_tmc_common import (
    AdapterType,
    HelperAdapterFactory,
    LivelinessProbeType,
    TMCCommand,
    TmcComponentManager,
)
from src.ska_tmc_common import InputParameter
from tests.settings import DummyComponentManager, State, logger


class DummyCommand(TMCCommand):
    def __init__(self, component_manager, logger, *args, **kwargs):
        super().__init__(component_manager, logger)
        self.condition = True

    def set_condition(self, value):
        self.condition = value

    def check_allowed(self):
        return self.condition


@pytest.fixture
def command_object():
    cm = TmcComponentManager(
        _input_parameter=InputParameter(None),
        logger=logger,
        _liveliness_probe=LivelinessProbeType.NONE,
        _event_receiver=False,
    )
    dummy_command = DummyCommand(cm, logger)
    return dummy_command


conditions = [(True, True), (False, False)]


@pytest.mark.parametrize("value,result", conditions)
def test_check_allowed(command_object, value, result):
    command_object.set_condition(value)
    return_value = command_object.check_allowed()
    assert return_value == result


def test_adapter_creation(command_object: DummyCommand):
    device = "src/tmc/common"
    start_time = time.time()
    command_object.adapter_factory = HelperAdapterFactory()
    adapter = command_object.adapter_creation_retry(
        device_name=device,
        adapter_type=AdapterType.BASE,
        start_time=start_time,
        timeout=10,
    )
    assert adapter.dev_name == "src/tmc/common"


def test_adapter_creation_failure(command_object: DummyCommand):
    device = "src/tmc/common"
    start_time = time.time()
    with pytest.raises(DevFailed):
        command_object.adapter_creation_retry(
            device_name=device,
            adapter_type=AdapterType.BASE,
            start_time=start_time,
            timeout=10,
        )


def test_command_with_transitional_obsstate(task_callback):
    cm = DummyComponentManager(
        _input_parameter=InputParameter(None),
        logger=logger,
        _liveliness_probe=LivelinessProbeType.NONE,
        _event_receiver=False,
        transitional_obsstate=True,
    )
    cm.state = State.NORMAL
    cm.invoke_command(True, task_callback=task_callback)
    time.sleep(2)
    task_callback.assert_against_call(
        status=TaskStatus.QUEUED,
    )
    cm.state = State.TRANSITIONAL
    time.sleep(0.5)
    cm.state = State.CHANGED
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED, result=ResultCode.OK
    )
