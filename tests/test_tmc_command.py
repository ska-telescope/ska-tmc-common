import pytest
from ska_tango_base.commands import ResultCode

from ska_tmc_common.op_state_model import TMCOpStateModel
from ska_tmc_common.tmc_command import TMCCommand
from ska_tmc_common.tmc_component_manager import TmcComponentManager
from tests.settings import logger


class DummyCommand(TMCCommand):
    def __init__(self, target, *args, logger=None, **kwargs):
        super().__init__(self, target, args, logger, kwargs)
        self.condition = True

    def set_condition(self, value):
        self.condition = value

    def check_allowed(self):
        return self.condition


@pytest.fixture
def command_object():

    op_state_model = TMCOpStateModel(logger)
    cm = TmcComponentManager(
        op_state_model,
        logger=logger,
        _monitoring_loop=False,
        _event_receiver=False,
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
    print(logger)
    result = command_object.generate_command_result(
        ResultCode.OK, "Test Message"
    )
    assert result == (ResultCode.OK, "Test Message")
