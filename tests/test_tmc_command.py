import pytest
from ska_tango_base.commands import ResultCode

from ska_tmc_common.tmc_command import TMCCommand
from tests.settings import logger


class DummyCommand(TMCCommand):
    def __init__(self, logger):
        super().__init__(logger)
        self.condition = True

    def set_condition(self, value):
        self.condition = value

    def check_allowed(self):
        return self.condition


@pytest.fixture
def command_object():
    dummy_command = DummyCommand(logger)

    return dummy_command


conditions = [(True, True), (False, False)]


@pytest.mark.parametrize("value,result", conditions)
def test_check_allowed(command_object, value, result):
    command_object.set_condition(value)
    return_value = command_object.check_allowed()
    assert return_value == result


def test_generate_command_result(command_object):
    print(logger)
    result = command_object.generate_command_result(
        ResultCode.OK, "Test Message"
    )
    assert result == (ResultCode.OK, "Test Message")
