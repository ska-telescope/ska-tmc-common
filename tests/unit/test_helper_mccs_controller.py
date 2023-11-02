import json

import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState

from ska_tmc_common import DevFactory, FaultType
from tests.settings import HELPER_MCCS_CONTROLLER

commands_with_argin = ["Allocate", "Release"]
commands_without_argin = ["On", "Off"]


@pytest.mark.parametrize("command", commands_with_argin)
def test_mccs_controller_commands_with_argument(tango_context, command):
    dev_factory = DevFactory()
    mccs_controller_device = dev_factory.get_device(HELPER_MCCS_CONTROLLER)
    result, unique_id = mccs_controller_device.command_inout(command, "1")
    assert result[0] == ResultCode.QUEUED
    assert unique_id[0].endswith(command)


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


def test_allocate_stuck_in_intermediate_state(tango_context):
    dev_factory = DevFactory()
    mccs_controller_device = dev_factory.get_device(HELPER_MCCS_CONTROLLER)
    defect = {
        "enabled": True,
        "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
        "result": ResultCode.FAILED,
        "intermediate_state": ObsState.RESOURCING,
    }
    mccs_controller_device.SetDefective(json.dumps(defect))
    result, _ = mccs_controller_device.command_inout("Allocate", "")
    assert result[0] == ResultCode.QUEUED
    mccs_controller_device.SetDefective(json.dumps({"enabled": False}))


def test_restart_subarray_command(tango_context):
    dev_factory = DevFactory()
    mccs_controller_device = dev_factory.get_device(HELPER_MCCS_CONTROLLER)
    subarray_id = 1  # Provide the subarray ID as an argument to the RestartSubarray command
    result = mccs_controller_device.command_inout(
        "RestartSubarray", subarray_id
    )
    assert result[0] == ResultCode.QUEUED
