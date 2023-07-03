import json

import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from tango import DevFailed

from ska_tmc_common import DevFactory, FaultType
from tests.settings import SDP_LEAF_NODE_DEVICE

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
    result, message = subarray_leaf_device.command_inout(command, "")
    assert result[0] == ResultCode.OK
    assert message[0] == ""


@pytest.mark.parametrize("command", commands_without_argin)
def test_leaf_node_command_without_argument(tango_context, command):
    dev_factory = DevFactory()
    subarray_leaf_device = dev_factory.get_device(SDP_LEAF_NODE_DEVICE)
    result, message = subarray_leaf_device.command_inout(command)
    assert result[0] == ResultCode.OK
    assert message[0] == ""


def test_assign_resources_failed_result(tango_context):
    dev_factory = DevFactory()
    subarray_leaf_device = dev_factory.get_device(SDP_LEAF_NODE_DEVICE)
    defect = {
        "enabled": True,
        "fault_type": FaultType.FAILED_RESULT,
        "error_message": "Device is Defective, cannot process command completely.",
        "result": ResultCode.FAILED,
    }
    subarray_leaf_device.SetDefective(json.dumps(defect))
    result, message = subarray_leaf_device.AssignResources("")
    assert result[0] == ResultCode.FAILED
    assert (
        message[0] == "Device is Defective, cannot process command completely."
    )
    subarray_leaf_device.SetDefective(json.dumps({"enabled": False}))


def test_assign_resources_stuck_in_intermediate_state(tango_context):
    dev_factory = DevFactory()
    subarray_leaf_device = dev_factory.get_device(SDP_LEAF_NODE_DEVICE)
    defect = {
        "enabled": True,
        "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
        "result": ResultCode.FAILED,
        "intermediate_state": ObsState.RESOURCING,
    }
    subarray_leaf_device.SetDefective(json.dumps(defect))
    result, _ = subarray_leaf_device.AssignResources("")
    assert result[0] == ResultCode.QUEUED
    assert subarray_leaf_device.obsState == ObsState.RESOURCING
    subarray_leaf_device.SetDefective(json.dumps({"enabled": False}))


def test_assign_resources_command_not_allowed(tango_context):
    dev_factory = DevFactory()
    subarray_leaf_device = dev_factory.get_device(SDP_LEAF_NODE_DEVICE)
    defect = {
        "enabled": True,
        "fault_type": FaultType.COMMAND_NOT_ALLOWED,
        "error_message": "Device is stuck in Resourcing state",
        "result": ResultCode.FAILED,
    }
    subarray_leaf_device.SetDefective(json.dumps(defect))
    with pytest.raises(DevFailed):
        subarray_leaf_device.AssignResources("")

    subarray_leaf_device.SetDefective(json.dumps({"enabled": False}))
