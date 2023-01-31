import time

import pytest
from ska_tango_base.commands import ResultCode

from ska_tmc_common.adapters import AdapterType
from ska_tmc_common.enum import LivelinessProbeType
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)
from ska_tmc_common.tmc_command import TMCCommand
from ska_tmc_common.tmc_component_manager import TmcComponentManager
from src.ska_tmc_common.input import InputParameter
from tests.settings import logger


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


def test_generate_command_result(command_object):
    result = command_object.generate_command_result(
        ResultCode.OK, "Test Message"
    )
    assert result == (ResultCode.OK, "Test Message")


@pytest.mark.test
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


@pytest.mark.test1
def test_adapter_creation_failure(command_object: DummyCommand):
    device = "src/tmc/common"
    start_time = time.time()
    result, error = command_object.adapter_creation_retry(
        device_name=device,
        adapter_type=AdapterType.BASE,
        start_time=start_time,
        timeout=10,
    )
    assert "Error in creating adapter for src/tmc/common" in error
