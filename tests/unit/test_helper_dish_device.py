import json
import time

import pytest
from ska_tango_base.commands import ResultCode

from ska_tmc_common import DevFactory
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
    assert not dish_device.defective
    dish_device.SetDefective(True)
    assert dish_device.defective


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


@pytest.mark.parametrize("command", commands)
def test_dish_commands(tango_context, command):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    result, message = dish_device.command_inout(command)
    command_call_info = dish_device.commandCallInfo
    assert command_call_info[0] == (command, "")
    assert result[0] == ResultCode.OK
    assert message[0] == ""


@pytest.mark.parametrize("command", commands)
def test_dish_command_defective(tango_context, command):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    dish_device.SetDefective(True)
    result, message = dish_device.command_inout(command)
    assert result[0] == ResultCode.FAILED
    assert message[0] == "Device is Defective, cannot process command."


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
    dish_device.SetDefective(True)
    result, message = dish_device.command_inout("ConfigureBand2", "")
    assert result[0] == ResultCode.FAILED
    assert message[0] == "Device is Defective, cannot process command."


def test_Reset_command_defective(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    dish_device.SetDefective(True)
    result, message = dish_device.Reset()
    assert result[0] == ResultCode.OK


@pytest.mark.parametrize("command", configure_commands)
def test_Configure_command(tango_context, command):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    dish_device.command_inout(command, "")
    time.sleep(0.5)
    assert dish_device.dishmode == DishMode.CONFIG
