import json

import pytest
from ska_tango_base.commands import ResultCode
from tango import DevFailed

from ska_tmc_common import DevFactory
from tests.settings import (
    COMMAND_NOT_ALLOWED_DEFECT,
    DISH_DEVICE,
    FAILED_RESULT_DEFECT,
)

COMMANDS = [
    "SetStandbyFPMode",
    "SetStandbyLPMode",
    "SetOperateMode",
    "SetStowMode",
    "Slew",
    "Scan",
    "AbortCommands",
    "Reset",
    "Configure",
    "ConfigureBand1",
    "ConfigureBand2",
    "ConfigureBand3",
    "ConfigureBand4",
    "ConfigureBand5a",
    "ConfigureBand5b",
]
COMMANDS_WITHOUT_INPUT = [
    "SetStandbyFPMode",
    "SetStandbyLPMode",
    "SetOperateMode",
    "SetStowMode",
    "Slew",
    "Scan",
    "AbortCommands",
    "Reset",
]
COMMANDS_WITH_INPUT = [
    "Configure",
    "ConfigureBand1",
    "ConfigureBand2",
    "ConfigureBand3",
    "ConfigureBand4",
    "ConfigureBand5a",
    "ConfigureBand5b",
]


def test_set_delay(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    dish_device.SetDelay('{"Configure": 3}')
    command_delay_info = json.loads(dish_device.commandDelayInfo)
    assert command_delay_info["Configure"] == 3


def test_state_transition(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(DISH_DEVICE)
    subarray_device.AddTransition('[["TRACK", 0.1]]')
    assert subarray_device.obsStateTransitionDuration == '[["TRACK", 0.1]]'


@pytest.mark.parametrize("command", COMMANDS_WITHOUT_INPUT)
def test_dish_commands_without_input(tango_context, command):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    result, message = dish_device.command_inout(command)
    command_call_info = dish_device.commandCallInfo
    assert command_call_info[0] == (command, "")
    assert result[0] == ResultCode.OK
    assert message[0] == ""


@pytest.mark.parametrize("command", COMMANDS_WITH_INPUT)
def test_dish_commands_with_input(tango_context, command):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    result, message = dish_device.command_inout(command, "")
    assert result[0] == ResultCode.OK
    assert message[0] == ""


@pytest.mark.parametrize("command_to_check", COMMANDS_WITHOUT_INPUT)
def test_command_without_argin_failed_result(tango_context, command_to_check):
    # import pdb
    # pdb.set_trace()
    dev_factory = DevFactory()
    # dish_device = dev_factory.get_device(DISH_DEVICE)
    dish_device = dev_factory.get_device(DISH_DEVICE)
    dish_device.SetDefective(json.dumps(FAILED_RESULT_DEFECT))
    result, message = dish_device.command_inout(command_to_check)
    assert result[0] == ResultCode.FAILED
    assert (
        message[0] == "Device is defective, cannot process command completely."
    )
    dish_device.SetDefective(json.dumps({"enabled": False}))


@pytest.mark.parametrize("command_to_check", COMMANDS_WITH_INPUT)
def test_command_with_argin_failed_result(tango_context, command_to_check):
    # import pdb
    # pdb.set_trace()
    dev_factory = DevFactory()
    # dish_device = dev_factory.get_device(DISH_DEVICE)
    dish_device = dev_factory.get_device(DISH_DEVICE)
    dish_device.SetDefective(json.dumps(FAILED_RESULT_DEFECT))
    result, message = dish_device.command_inout(command_to_check, "")
    assert result[0] == ResultCode.FAILED
    assert (
        message[0] == "Device is defective, cannot process command completely."
    )
    dish_device.SetDefective(json.dumps({"enabled": False}))


def test_Abort_commands(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    result, message = dish_device.command_inout("AbortCommands")
    assert result[0] == ResultCode.OK
    assert message[0] == ""


@pytest.mark.parametrize("command_to_check", COMMANDS)
def test_dish_commands_command_not_allowed(tango_context, command_to_check):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    # Set the device to the defective state with COMMAND_NOT_ALLOWED fault
    dish_device.SetDefective(json.dumps(COMMAND_NOT_ALLOWED_DEFECT))
    # Attempt to execute the command and expect the DevFailed exception
    with pytest.raises(DevFailed):
        dish_device.command_inout(command_to_check)
    # Clear the defect and ensure the command can be executed when not defective
    dish_device.SetDefective(json.dumps({"enabled": False}))
