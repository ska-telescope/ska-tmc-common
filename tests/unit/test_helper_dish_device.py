import pytest
from ska_tango_base.commands import ResultCode

from ska_tmc_common import DevFactory
from tests.settings import DISH_DEVICE

commands = [
    "Standby",
    "SetOperateMode",
    "SetStowMode",
    "SetStandbyFPMode",
    "SetStandbyLPMode",
    "Track",
]


def test_set_defective(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    assert not dish_device.defective
    dish_device.SetDefective(True)
    assert dish_device.defective


@pytest.mark.parametrize("command", commands)
def test_dish_commands(tango_context, command):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    result, message = getattr(dish_device, command)()
    assert result[0] == ResultCode.OK
    assert message[0] == ""


@pytest.mark.parametrize("command", commands)
def test_dish_command_defective(tango_context, command):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    dish_device.SetDefective(True)
    result, message = getattr(dish_device, command)()
    assert result[0] == ResultCode.FAILED
    assert message[0] == "Device is Defective, cannot process command."


def test_Abort_commands(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    result, message = getattr(dish_device, "AbortCommands")()
    assert result[0] == ResultCode.OK
    assert message[0] == ""
