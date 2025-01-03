import json

import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import AdminMode, ObsState
from tango import DevFailed, EventType

from ska_tmc_common import DevFactory, FaultType
from tests.settings import (
    FAILED_RESULT_DEFECT,
    FAILED_RESULT_DEFECT_EXCEPTION,
    SDP_LEAF_NODE_DEVICE,
    wait_for_obstate,
)

commands_with_argin = ["AssignResources", "Scan", "Configure"]
commands_without_argin = [
    "On",
    "Off",
    "ReleaseAllResources",
    "EndScan",
    "Restart",
    "Standby",
    "End",
    "Abort",
    "ReleaseAllResources",
]


@pytest.mark.parametrize("command", commands_with_argin)
def test_leaf_node_command_with_argument(tango_context, command):
    dev_factory = DevFactory()
    subarray_leaf_device = dev_factory.get_device(SDP_LEAF_NODE_DEVICE)
    subarray_leaf_device.adminMode = AdminMode.ONLINE
    result, command_id = subarray_leaf_device.command_inout(command, "")
    assert result[0] == ResultCode.QUEUED
    assert isinstance(command_id[0], str)


def test_set_obs_state_transition(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SDP_LEAF_NODE_DEVICE)
    subarray_device.adminMode = AdminMode.ONLINE
    subarray_device.AddTransition('[["CONFIGURING", 0.1]]')
    assert (
        subarray_device.obsStateTransitionDuration == '[["CONFIGURING", 0.1]]'
    )


def test_reset_obs_state_transition(tango_context):
    dev_factory = DevFactory()
    subarray_leaf_device = dev_factory.get_device(SDP_LEAF_NODE_DEVICE)
    subarray_leaf_device.adminMode = AdminMode.ONLINE
    subarray_leaf_device.AddTransition('[["CONFIGURING", 0.1]]')
    assert (
        subarray_leaf_device.obsStateTransitionDuration
        == '[["CONFIGURING", 0.1]]'
    )
    subarray_leaf_device.ResetTransitions()
    assert subarray_leaf_device.obsStateTransitionDuration == "[]"


def test_obs_state_tranisition_for_configure(tango_context):
    dev_factory = DevFactory()
    subarray_leaf_device = dev_factory.get_device(SDP_LEAF_NODE_DEVICE)
    subarray_leaf_device.adminMode = AdminMode.ONLINE
    subarray_leaf_device.AddTransition('[["READY", 0.0]]')
    _, _ = subarray_leaf_device.Configure("")
    wait_for_obstate(subarray_leaf_device, ObsState.READY)
    assert subarray_leaf_device.obsState == ObsState.READY


def test_obs_state_tranisition_for_assignresources(tango_context):
    dev_factory = DevFactory()
    subarray_leaf_device = dev_factory.get_device(SDP_LEAF_NODE_DEVICE)
    subarray_leaf_device.adminMode = AdminMode.ONLINE
    subarray_leaf_device.AddTransition('[["READY", 0.0]]')
    _, _ = subarray_leaf_device.AssignResources("")
    wait_for_obstate(subarray_leaf_device, ObsState.READY)
    assert subarray_leaf_device.obsState == ObsState.READY


def test_clear_commandCallInfo(tango_context):
    dev_factory = DevFactory()
    subarray_leaf_device = dev_factory.get_device(SDP_LEAF_NODE_DEVICE)
    subarray_leaf_device.adminMode = AdminMode.ONLINE
    _, _ = subarray_leaf_device.command_inout("Configure", "")
    subarray_leaf_device.command_inout("ClearCommandCallInfo")
    command_call_info = subarray_leaf_device.commandCallInfo
    assert command_call_info == ()


@pytest.mark.parametrize("command", commands_without_argin)
def test_leaf_node_command_without_argument(tango_context, command):
    dev_factory = DevFactory()
    subarray_leaf_device = dev_factory.get_device(SDP_LEAF_NODE_DEVICE)
    subarray_leaf_device.adminMode = AdminMode.ONLINE
    result, command_id = subarray_leaf_device.command_inout(command)
    assert result[0] == ResultCode.QUEUED
    assert isinstance(command_id[0], str)


def test_assign_resources_failed_result(tango_context):
    dev_factory = DevFactory()
    subarray_leaf_device = dev_factory.get_device(SDP_LEAF_NODE_DEVICE)
    subarray_leaf_device.adminMode = AdminMode.ONLINE
    subarray_leaf_device.SetDefective(json.dumps(FAILED_RESULT_DEFECT))
    result, command_id = subarray_leaf_device.AssignResources("")
    assert result[0] == ResultCode.FAILED
    assert FAILED_RESULT_DEFECT_EXCEPTION in command_id[0]
    subarray_leaf_device.SetDefective(json.dumps({"enabled": False}))


def test_assign_resources_long_running_exception(
    tango_context, group_callback
):
    dev_factory = DevFactory()
    subarray_leaf_device = dev_factory.get_device(SDP_LEAF_NODE_DEVICE)
    defect = {
        "enabled": True,
        "fault_type": FaultType.LONG_RUNNING_EXCEPTION,
        "error_message": "Exception occurred",
        "result": ResultCode.FAILED,
    }
    subarray_leaf_device.adminMode = AdminMode.ONLINE
    subarray_leaf_device.SetDefective(json.dumps(defect))
    subarray_leaf_device.subscribe_event(
        "longRunningCommandResult",
        EventType.CHANGE_EVENT,
        group_callback["longRunningCommandResult"],
    )
    result, command_id = subarray_leaf_device.AssignResources("")
    assert result[0] == ResultCode.QUEUED
    assert "AssignResources" in command_id[0]
    group_callback["longRunningCommandResult"].assert_change_event(
        (command_id[0], json.dumps((ResultCode.FAILED, "Exception occurred"))),
        lookahead=3,
    )
    subarray_leaf_device.SetDefective(json.dumps({"enabled": False}))


def test_assign_resources_command_not_allowed_after_queuing(
    tango_context, group_callback
):
    dev_factory = DevFactory()
    subarray_leaf_device = dev_factory.get_device(SDP_LEAF_NODE_DEVICE)
    defect = {
        "enabled": True,
        "fault_type": FaultType.COMMAND_NOT_ALLOWED_AFTER_QUEUING,
    }
    subarray_leaf_device.adminMode = AdminMode.ONLINE
    subarray_leaf_device.SetDefective(json.dumps(defect))
    subarray_leaf_device.subscribe_event(
        "longRunningCommandResult",
        EventType.CHANGE_EVENT,
        group_callback["longRunningCommandResult"],
    )
    result, command_id = subarray_leaf_device.AssignResources("")
    assert result[0] == ResultCode.QUEUED
    assert "AssignResources" in command_id[0]
    group_callback["longRunningCommandResult"].assert_change_event(
        (
            command_id[0],
            json.dumps((ResultCode.NOT_ALLOWED, "Command is not allowed")),
        ),
        lookahead=3,
    )
    subarray_leaf_device.SetDefective(json.dumps({"enabled": False}))


def test_assign_resources_command_not_allowed_exception_after_queuing(
    tango_context, group_callback
):
    dev_factory = DevFactory()
    subarray_leaf_device = dev_factory.get_device(SDP_LEAF_NODE_DEVICE)
    subarray_leaf_device.adminMode = AdminMode.ONLINE
    defect = {
        "enabled": True,
        "fault_type": FaultType.COMMAND_NOT_ALLOWED_EXCEPTION_AFTER_QUEUING,
        "error_message": "Exception occurred",
    }
    subarray_leaf_device.SetDefective(json.dumps(defect))
    subarray_leaf_device.subscribe_event(
        "longRunningCommandResult",
        EventType.CHANGE_EVENT,
        group_callback["longRunningCommandResult"],
    )
    result, command_id = subarray_leaf_device.AssignResources("")
    assert result[0] == ResultCode.QUEUED
    assert "AssignResources" in command_id[0]
    group_callback["longRunningCommandResult"].assert_change_event(
        (
            command_id[0],
            json.dumps(
                (
                    ResultCode.REJECTED,
                    "Exception from 'is_cmd_allowed' method: "
                    + "Exception occurred",
                )
            ),
        ),
        lookahead=3,
    )
    subarray_leaf_device.SetDefective(json.dumps({"enabled": False}))


def test_assign_resources_stuck_in_intermediate_state(tango_context):
    dev_factory = DevFactory()
    subarray_leaf_device = dev_factory.get_device(SDP_LEAF_NODE_DEVICE)
    subarray_leaf_device.adminMode = AdminMode.ONLINE
    defect = {
        "enabled": True,
        "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
        "result": ResultCode.FAILED,
        "error_message": "Device is stuck in Resourcing state",
        "intermediate_state": ObsState.RESOURCING,
    }
    subarray_leaf_device.SetDefective(json.dumps(defect))
    result, _ = subarray_leaf_device.AssignResources("")
    assert result[0] == ResultCode.QUEUED
    wait_for_obstate(subarray_leaf_device, ObsState.RESOURCING)
    assert subarray_leaf_device.obsState == ObsState.RESOURCING
    subarray_leaf_device.SetDefective(json.dumps({"enabled": False}))


def test_assign_resources_command_not_allowed(tango_context):
    dev_factory = DevFactory()
    subarray_leaf_device = dev_factory.get_device(SDP_LEAF_NODE_DEVICE)
    subarray_leaf_device.adminMode = AdminMode.ONLINE
    defect = {
        "enabled": True,
        "fault_type": FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING,
        "error_message": "Device is stuck in Resourcing state",
        "result": ResultCode.FAILED,
    }
    subarray_leaf_device.SetDefective(json.dumps(defect))
    with pytest.raises(DevFailed):
        subarray_leaf_device.AssignResources("")

    subarray_leaf_device.SetDefective(json.dumps({"enabled": False}))
