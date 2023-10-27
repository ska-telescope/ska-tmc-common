import json

import pytest
from ska_tango_base.commands import ResultCode
from tango import DevFailed

from ska_tmc_common import DevFactory
from tests.settings import (
    COMMAND_NOT_ALLOWED_DEFECT,
    DISH_LN_DEVICE,
    FAILED_RESULT_DEFECT,
)

COMMANDS = [
    "SetStandbyFPMode",
    "SetStandbyLPMode",
    "SetOperateMode",
    "SetStowMode",
    "Off",
    "AbortCommands",
    "Configure",
    "Scan",
]
COMMANDS_WITHOUT_INPUT = [
    "SetStandbyFPMode",
    "SetStandbyLPMode",
    "SetOperateMode",
    "SetStowMode",
    "Off",
    "AbortCommands",
    "Scan",
]
COMMANDS_WITH_INPUT = [
    "Configure",
]


@pytest.mark.parametrize("command", COMMANDS_WITHOUT_INPUT)
def test_dish_commands_without_input(tango_context, command):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_LN_DEVICE)
    result, message = dish_device.command_inout(command)
    command_call_info = dish_device.commandCallInfo
    assert command_call_info[0] == (command, "")
    assert result[0] == ResultCode.OK
    assert message[0] == ""


@pytest.mark.parametrize("command", COMMANDS_WITH_INPUT)
def test_dish_commands_with_input(tango_context, command):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_LN_DEVICE)
    result, message = dish_device.command_inout(command, "")
    assert result[0] == ResultCode.OK
    assert message[0] == ""


@pytest.mark.parametrize("command_to_check", COMMANDS_WITHOUT_INPUT)
def test_command_without_argin_failed_result(tango_context, command_to_check):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_LN_DEVICE)
    dish_device.SetDefective(json.dumps(FAILED_RESULT_DEFECT))
    result, message = dish_device.command_inout(command_to_check)
    assert result[0] == ResultCode.FAILED
    assert (
        message[0] == "Device is defective, cannot process command completely."
    )
    dish_device.SetDefective(json.dumps({"enabled": False}))


@pytest.mark.parametrize("command_to_check", COMMANDS_WITH_INPUT)
def test_command_with_argin_failed_result(tango_context, command_to_check):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_LN_DEVICE)
    dish_device.SetDefective(json.dumps(FAILED_RESULT_DEFECT))
    result, message = dish_device.command_inout(command_to_check, "")
    assert result[0] == ResultCode.FAILED
    assert (
        message[0] == "Device is defective, cannot process command completely."
    )
    dish_device.SetDefective(json.dumps({"enabled": False}))


def test_Abort_commands(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_LN_DEVICE)
    result, message = dish_device.command_inout("AbortCommands")
    assert result[0] == ResultCode.OK
    assert message[0] == ""


@pytest.mark.parametrize("command_to_check", COMMANDS)
def test_dish_commands_command_not_allowed(tango_context, command_to_check):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_LN_DEVICE)
    # Set the device to the defective state with COMMAND_NOT_ALLOWED fault
    dish_device.SetDefective(json.dumps(COMMAND_NOT_ALLOWED_DEFECT))
    # Attempt to execute the command and expect the DevFailed exception
    with pytest.raises(DevFailed):
        dish_device.command_inout(command_to_check)
    # Clear the defect and ensure the command can be executed when not
    # defective
    dish_device.SetDefective(json.dumps({"enabled": False}))


def test_SetKValue_command_dishln(tango_context):
    """
    This test case invokes command on dish leaf node device
    and checks whether the attributes are populated with
    relevant k value or not.
    """
    dev_factory = DevFactory()
    dishln_device = dev_factory.get_device(DISH_LN_DEVICE)

    return_code, _ = dishln_device.SetKValue(5)
    return_code[0] = ResultCode.OK

    assert dishln_device.kValue == 5


def test_dishln_actual_pointing(tango_context, json_factory):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_LN_DEVICE)
    configure_input = json_factory("dishleafnode_configure")
    configure_input1 = json.loads(configure_input)
    ra = configure_input1["pointing"]["target"]["ra"]
    dec = configure_input1["pointing"]["target"]["dec"]
    result, message = dish_device.Configure(configure_input)
    actual_pointing_list = json.loads(dish_device.actualPointing)
    assert actual_pointing_list[1:] == [ra, dec]
    assert result[0] == ResultCode.OK
    assert message[0] == ""
