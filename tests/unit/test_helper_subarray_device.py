import json

import pytest
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode

from ska_tmc_common import DevFactory
from tests.settings import DEFAULT_DEFECT_SETTINGS, SUBARRAY_DEVICE

commands_with_argin = [
    "AssignResources",
    "Scan",
    "Configure",
    "ReleaseResources",
]
commands_without_argin = [
    "On",
    "Off",
    "ReleaseAllResources",
    "EndScan",
    "ObsReset",
    "Restart",
    "Standby",
    "End",
    "Abort",
    "Restart",
    "GoToIdle",
]


def test_command_call_info(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    _, _ = subarray_device.command_inout("AssignResources", "")
    command_call_info_len = len(subarray_device.commandCallInfo)
    _, _ = subarray_device.command_inout("Configure", "")
    command_call_info_len = command_call_info_len + 1
    assert command_call_info_len == 2
    command_call_info = subarray_device.commandCallInfo
    assert command_call_info[command_call_info_len - 1] == ("Configure", "")


def test_obs_state_transition(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    subarray_device.AddTransition('[["CONFIGURING", 0.1]]')
    assert (
        subarray_device.obsStateTransitionDuration == '[["CONFIGURING", 0.1]]'
    )


def test_set_delay(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    subarray_device.SetDelay('{"Configure": 3}')
    command_delay_info = json.loads(subarray_device.commandDelayInfo)
    assert command_delay_info["Configure"] == 3


def test_clear_commandCallInfo(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    _, _ = subarray_device.command_inout("Configure", "")
    subarray_device.command_inout("ClearCommandCallInfo")
    command_call_info = subarray_device.commandCallInfo
    assert command_call_info == ()


def test_set_defective(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    subarray_device.SetDefective(json.dumps(DEFAULT_DEFECT_SETTINGS))
    result, message = subarray_device.command_inout("AssignResources", "")
    assert result[0] == ResultCode.FAILED
    assert message[0] == "Default exception."


def test_set_raise_exception(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    assert not subarray_device.raiseException
    subarray_device.SetRaiseException(True)
    assert subarray_device.raiseException


@pytest.mark.parametrize("command", commands_with_argin)
def test_command_with_argin(tango_context, command):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    result, command_id = subarray_device.command_inout(command, "")
    command_call_info = subarray_device.commandCallInfo
    assert command_call_info[0] == (command, "")
    assert result[0] == ResultCode.QUEUED
    assert isinstance(command_id[0], str)


@pytest.mark.parametrize("command", commands_without_argin)
def test_command_without_argin(tango_context, command):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    result, command_id = subarray_device.command_inout(command)
    assert result[0] == ResultCode.QUEUED
    assert isinstance(command_id[0], str)


def test_assign_resources_defective(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    subarray_device.SetDefective(json.dumps(DEFAULT_DEFECT_SETTINGS))
    result, message = subarray_device.AssignResources("")
    assert result[0] == ResultCode.FAILED
    assert message[0] == "Default exception."


def test_scan_command(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    result, command_id = subarray_device.Scan("")
    assert result[0] == ResultCode.QUEUED
    assert subarray_device.obsstate == ObsState.SCANNING
    assert isinstance(command_id[0], str)


def test_release_resources_defective(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    subarray_device.SetDefective(json.dumps(DEFAULT_DEFECT_SETTINGS))
    result, message = subarray_device.ReleaseAllResources()
    assert result[0] == ResultCode.FAILED
    assert message[0] == "Default exception."


def test_assign_resources_raise_exception(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    subarray_device.SetRaiseException(True)
    result, message = subarray_device.AssignResources("")
    assert result[0] == ResultCode.QUEUED
    assert subarray_device.obsstate == ObsState.RESOURCING


def test_release_resources_raise_exception(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    subarray_device.SetRaiseException(True)
    result, message = subarray_device.ReleaseAllResources()
    assert result[0] == ResultCode.QUEUED
    assert subarray_device.obsstate == ObsState.RESOURCING


def test_assigned_resources_attribute_with_change_event(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    subarray_device.SetDirectassignedResources('{"channels": [0]}')
    assigned_resources = subarray_device.read_attribute(
        "assignedResources"
    ).value
    assert assigned_resources == '{"channels": [0]}'
