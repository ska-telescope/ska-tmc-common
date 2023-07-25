import json
import time

import pytest
from ska_tango_base.commands import ResultCode
from tango import DevFailed

from ska_tmc_common import DevFactory, FaultType
from ska_tmc_common.enum import DishMode
from tests.settings import DISH_DEVICE

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


def test_set_defective(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    defect = {
        "enabled": True,
        "fault_type": FaultType.FAILED_RESULT,
        "error_message": "Device is defective, cannot process command.completely.",
        "result": ResultCode.FAILED,
    }
    dish_device.SetDefective(json.dumps(defect))
    assert dish_device.defective
    dish_device.SetDefective(json.dumps({"enabled": False}))


@pytest.mark.akiii
@pytest.mark.parametrize("command", commands)
def test_dish_commands(tango_context, command):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    result, message = dish_device.command_inout(command)
    assert result[0] == ResultCode.OK
    assert message[0] == ""


@pytest.mark.parametrize("command_to_check", configure_commands)
def test_configure_command_failed_result(tango_context, command_to_check):
    # import pdb
    # pdb.set_trace()
    dev_factory = DevFactory()
    # dish_device = dev_factory.get_device(DISH_DEVICE)
    dish_device = dev_factory.get_device(DISH_DEVICE)
    defect = {
        "enabled": True,
        "fault_type": FaultType.FAILED_RESULT,
        "error_message": "Device is Defective, cannot process command completely.",
        "result": ResultCode.FAILED,
    }
    dish_device.SetDefective(json.dumps(defect))
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


def test_Configure_commands(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    result, message = dish_device.command_inout("ConfigureBand2", "")
    assert result[0] == ResultCode.OK
    assert message[0] == ""


def test_Configure_command_defective(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    defect = {
        "enabled": True,
        "fault_type": FaultType.FAILED_RESULT,
        "error_message": "Device is defective, cannot process command.",
        "result": ResultCode.FAILED,
    }
    dish_device.SetDefective(json.dumps(defect))
    result, message = dish_device.command_inout("ConfigureBand2", "")
    assert result[0] == ResultCode.FAILED
    assert message[0] == "Device is defective, cannot process command."
    dish_device.SetDefective(json.dumps({"enabled": False}))


def test_Reset_command_defective(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    defect = {
        "enabled": True,
        "fault_type": FaultType.FAILED_RESULT,
        "error_message": "Device is defective, cannot process command.",
        "result": ResultCode.FAILED,
    }
    dish_device.SetDefective(json.dumps(defect))
    result, message = dish_device.Reset()
    assert result[0] == ResultCode.OK
    dish_device.SetDefective(json.dumps({"enabled": False}))


@pytest.mark.failed
@pytest.mark.parametrize("command", configure_commands)
def test_Configure_command(tango_context, command):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    dish_device.SetDefective(json.dumps({"enabled": False}))
    dish_device.command_inout(command, "")
    time.sleep(0.5)
    assert dish_device.dishmode == DishMode.CONFIG


@pytest.mark.parametrize("command_to_check", configure_commands)
def test_configure_commands_command_not_allowed(
    tango_context, command_to_check
):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    defect = {
        "enabled": True,
        "fault_type": FaultType.COMMAND_NOT_ALLOWED,
        "error_message": "Device is stuck in Resourcing state",
        "result": ResultCode.FAILED,
    }
    # Set the device to the defective state with COMMAND_NOT_ALLOWED fault
    dish_device.SetDefective(json.dumps(defect))
    # Attempt to execute the command and expect the DevFailed exception
    with pytest.raises(DevFailed):
        dish_device.command_inout(command_to_check)
    # Clear the defect and ensure the command can be executed when not defective
    dish_device.SetDefective(json.dumps({"enabled": False}))
