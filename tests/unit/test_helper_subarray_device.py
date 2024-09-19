import json
from operator import methodcaller

import pytest
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode

from ska_tmc_common import DevFactory, FaultType
from ska_tmc_common.test_helpers.constants import (
    ABORT,
    ASSIGN_RESOURCES,
    CONFIGURE,
    END,
    RELEASE_ALL_RESOURCES,
    RELEASE_RESOURCES,
    RESTART,
)
from ska_tmc_common.test_helpers.helper_subarray_device import (
    EmptySubArrayComponentManager,
)
from tests.settings import DEFAULT_DEFECT_SETTINGS, SUBARRAY_DEVICE, logger

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
    "Standby",
    "End",
    "GoToIdle",
]


@pytest.mark.parametrize(
    "command",
    [
        "assign",
        "release",
        "release_all",
        "configure",
        "end",
        "scan",
        "end_scan",
        "abort",
        "obsreset",
        "restart",
    ],
)
def test_empty_subarray_component_manager(command):
    cm = EmptySubArrayComponentManager(logger)
    match command:
        case "assign" | "configure" | "release" | "scan":
            command = methodcaller(command, "")
            result, message = command(cm)
        case _:
            command = methodcaller(command)
            result, message = command(cm)

    if command == "assign":
        assert cm.assigned_resources == ["0001"]
    elif command == "release_all":
        assert not cm.assigned_resources
    assert result == ResultCode.OK
    assert message == ""


def test_helper_subarray_device_attributes(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    assert subarray_device.commandInProgress == ""
    assert subarray_device.receiveAddresses == ""
    assert subarray_device.defective == json.dumps(
        {
            "enabled": False,
            "fault_type": FaultType.FAILED_RESULT,
            "error_message": "Default exception.",
            "result": ResultCode.FAILED,
        }
    )
    assert subarray_device.commandDelayInfo == json.dumps(
        {
            ASSIGN_RESOURCES: 2,
            CONFIGURE: 2,
            RELEASE_RESOURCES: 2,
            ABORT: 2,
            RESTART: 2,
            RELEASE_ALL_RESOURCES: 2,
            END: 2,
        }
    )
    assert not subarray_device.commandCallInfo
    assert subarray_device.obsStateTransitionDuration == json.dumps([])
    assert subarray_device.scanId == 0
    assert subarray_device.isSubsystemAvailable is True


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
    subarray_device.SetDelayInfo('{"Configure": 3}')
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
    result, command_id = subarray_device.command_inout("AssignResources", "")
    assert result[0] == ResultCode.FAILED
    assert "AssignResources" in command_id[0]


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
    result, command_id = subarray_device.AssignResources("")
    assert result[0] == ResultCode.FAILED
    assert "AssignResources" in command_id[0]


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
    result, command_id = subarray_device.ReleaseAllResources()
    assert result[0] == ResultCode.FAILED
    assert "ReleaseAllResources" in command_id[0]


def test_assigned_resources_attribute_with_change_event(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    subarray_device.SetDirectassignedResources('{"channels": [0]}')
    assigned_resources = subarray_device.read_attribute(
        "assignedResources"
    ).value
    assert assigned_resources == '{"channels": [0]}'
