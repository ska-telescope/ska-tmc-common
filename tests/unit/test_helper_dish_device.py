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

commands = [
    "Standby",
    "SetOperateMode",
    "SetStowMode",
    "SetStandbyFPMode",
    "SetStandbyLPMode",
    "Track",
]
configure_commands = [
    "ConfigureBand1",
    "ConfigureBand3",
    "ConfigureBand4",
    "ConfigureBand5a",
    "ConfigureBand5b",
]

defective_commands = [
    "SetStandbyFPMode",
    "SetStandbyLPMode",
    "SetOperateMode",
    "SetStowMode",
    "Configure",
    "ConfigureBand1",
    "ConfigureBand3",
    "ConfigureBand4",
    "ConfigureBand5a",
    "ConfigureBand5b",
    "Slew",
    "Scan",
    "AbortCommands" "Reset",
]


@pytest.mark.MS
def test_set_defective(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    dish_device.SetDefective(json.dumps(FAILED_RESULT_DEFECT))
    assert dish_device.defective == FAILED_RESULT_DEFECT
    dish_device.SetDefective(json.dumps({"enabled": False}))


@pytest.mark.parametrize("command", commands)
def test_dish_commands(tango_context, command):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    result, message = dish_device.command_inout(command)
    assert result[0] == ResultCode.OK
    assert message[0] == ""


@pytest.mark.parametrize("command_to_check", commands)
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
        message[0] == "Device is Defective, cannot process command completely."
    )
    dish_device.SetDefective(json.dumps({"enabled": False}))


@pytest.mark.parametrize("command_to_check", configure_commands)
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
        message[0] == "Device is Defective, cannot process command completely."
    )
    dish_device.SetDefective(json.dumps({"enabled": False}))


def test_Abort_commands(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    result, message = dish_device.command_inout("AbortCommands")
    assert result[0] == ResultCode.OK
    assert message[0] == ""


@pytest.mark.parametrize("command", configure_commands)
def test_Configure_command_defective(tango_context, command):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    dish_device.SetDefective(json.dumps(FAILED_RESULT_DEFECT))
    result, message = dish_device.command_inout(command, "")
    assert result[0] == ResultCode.OK


def test_Reset_command_defective(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    result, message = dish_device.Reset()
    assert result[0] == ResultCode.OK


@pytest.mark.parametrize("command", configure_commands)
def test_Configure_commands(tango_context, command):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    result, message = dish_device.command_inout(command, "")
    assert result[0] == ResultCode.OK
    assert message[0] == ""


@pytest.mark.parametrize("command_to_check", defective_commands)
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
