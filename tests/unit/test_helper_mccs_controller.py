import json

import pytest
from ska_tango_base.commands import ResultCode

from ska_tmc_common import DevFactory
from tests.settings import HELPER_MCCS_CONTROLLER

commands_with_argin = ["Allocate", "Release"]
commands_without_argin = ["On", "Off"]


@pytest.mark.parametrize("command", commands_with_argin)
def test_mccs_controller_commands_with_argument(tango_context, command):
    dev_factory = DevFactory()
    mccs_controller_device = dev_factory.get_device(HELPER_MCCS_CONTROLLER)
    result, message = mccs_controller_device.command_inout(command, "")
    assert result[0] == ResultCode.OK
    assert message[0] == ""


@pytest.mark.parametrize("command", commands_without_argin)
def test_mccs_controller_commands_without_argument(tango_context, command):
    dev_factory = DevFactory()
    mccs_controller_device = dev_factory.get_device(HELPER_MCCS_CONTROLLER)
    result, message = mccs_controller_device.command_inout(command)
    assert result[0] == ResultCode.OK
    assert message[0] == ""


@pytest.mark.parametrize("command", commands_with_argin)
def test_mccs_controller_command_defective(tango_context, command):
    dev_factory = DevFactory()
    mccs_controller_device = dev_factory.get_device(HELPER_MCCS_CONTROLLER)
    mccs_controller_device.SetDefective(json.dumps({"enabled": True}))
    result, message = mccs_controller_device.command_inout(command, "")
    assert result[0] == ResultCode.FAILED
    assert message[0] == "Default exception."


@pytest.mark.parametrize("command", commands_with_argin)
def test_mccs_controller_command_raise_exception(tango_context, command):
    dev_factory = DevFactory()
    mccs_controller_device = dev_factory.get_device(HELPER_MCCS_CONTROLLER)
    mccs_controller_device.SetRaiseException(True)
    result, message = mccs_controller_device.command_inout(command, "")
    assert result[0] == ResultCode.QUEUED
