import json
import time

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


@pytest.mark.parametrize("command", COMMANDS_WITHOUT_INPUT)
def test_dish_commands_without_input(tango_context, command):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_LN_DEVICE)
    result, message = dish_device.command_inout(command)
    command_call_info = dish_device.commandCallInfo
    assert command_call_info[0] == (command, "")
    assert result[0] == ResultCode.OK
    assert message[0] == ""


def test_dish_commands_with_input(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_LN_DEVICE)
    result, _ = dish_device.command_inout("Configure", "")
    assert result[0] == ResultCode.QUEUED


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


def test_command_with_argin_failed_result(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_LN_DEVICE)
    dish_device.SetDefective(json.dumps(FAILED_RESULT_DEFECT))
    result, message = dish_device.command_inout("Configure", "")
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


def test_SetKValue_command_dishln_defective(tango_context):
    """
    This test case invokes command on dish leaf node device
    and checks whether the attributes are populated with
    relevant k value or not.
    """
    dev_factory = DevFactory()
    dishln_device = dev_factory.get_device(DISH_LN_DEVICE)
    dishln_device.SetDefective(json.dumps(FAILED_RESULT_DEFECT))
    return_code, error_message = dishln_device.SetKValue(5)

    assert return_code[0] == ResultCode.FAILED
    assert (
        error_message[0]
        == "Device is defective, cannot process command completely."
    )

    dishln_device.SetDefective(json.dumps({"enabled": False}))


@pytest.mark.test
def test_to_check_kvalidationresult_push_event(tango_context):
    """
    This test case checks kValuvalidationResult event gets pushed after
    invoking SetDirectkValueValidationResult command.
    """
    dev_factory = DevFactory()
    dishln_device = dev_factory.get_device(DISH_LN_DEVICE)
    time.sleep(15)
    # Assert initial value is getting set
    assert dishln_device.kValueValidationResult == str(int(ResultCode.OK))
    # Assert command is working as expected
    dishln_device.SetDirectkValueValidationResult(str(int(ResultCode.FAILED)))
    assert dishln_device.kValueValidationResult == str(int(ResultCode.FAILED))
