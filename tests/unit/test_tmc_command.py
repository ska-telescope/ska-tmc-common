import logging
from typing import Optional

import pytest
from ska_tango_base.commands import ResultCode

from ska_tmc_common.tmc_command import TMCCommand
from ska_tmc_common.tmc_component_manager import TmcComponentManager
from src.ska_tmc_common.input import InputParameter
from tests.settings import logger


class DummyCommand(TMCCommand):
    def __init__(
        self, target, logger: Optional[logging.Logger] = None, *args, **kwargs
    ):
        # super().__init__(self, target, args, logger, kwargs)
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
        _liveliness_probe=False,
        _event_receiver=False,
        communication_state_callback=None,
        component_state_callback=None,
    )
    dummy_command = DummyCommand(cm, logger=logger)
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
