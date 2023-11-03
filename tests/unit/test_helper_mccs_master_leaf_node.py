import json

import pytest
from ska_tango_base.commands import ResultCode
from tango import DevFailed

from ska_tmc_common import DevFactory, FaultType
from tests.settings import HELPER_MCCS_MASTER_LEAF_NODE_DEVICE

commands_with_argin = ["AssignResources", "ReleaseAllResources"]
commands_without_argin = ["On", "Off"]


@pytest.mark.parametrize("command", commands_with_argin)
def test_mccs_master_leaf_node_commands_with_argument(tango_context, command):
    dev_factory = DevFactory()
    mccs_master_leaf_node_device = dev_factory.get_device(
        HELPER_MCCS_MASTER_LEAF_NODE_DEVICE
    )
    result, message = mccs_master_leaf_node_device.command_inout(command, "")
    assert result[0] == ResultCode.OK


@pytest.mark.parametrize("command", commands_without_argin)
def test_mccs_master_leaf_node_commands_without_argument(
    tango_context, command
):
    dev_factory = DevFactory()
    mccs_master_leaf_node_device = dev_factory.get_device(
        HELPER_MCCS_MASTER_LEAF_NODE_DEVICE
    )
    result, message = mccs_master_leaf_node_device.command_inout(command)
    assert result[0] == ResultCode.OK
    assert message[0] == ""


def test_assign_resources_failed_result(tango_context):
    dev_factory = DevFactory()
    mccs_master_leaf_node_device = dev_factory.get_device(
        HELPER_MCCS_MASTER_LEAF_NODE_DEVICE
    )
    defect = {
        "enabled": True,
        "fault_type": FaultType.FAILED_RESULT,
        "error_message": "Device is defective, cannot process command.completely.",
        "result": ResultCode.FAILED,
    }
    mccs_master_leaf_node_device.SetDefective(json.dumps(defect))
    result, message = mccs_master_leaf_node_device.AssignResources("")
    assert result[0] == ResultCode.FAILED
    assert (
        message[0] == "Device is defective, cannot process command.completely."
    )
    mccs_master_leaf_node_device.SetDefective(json.dumps({"enabled": False}))


def test_assign_resources_command_not_allowed(tango_context):
    dev_factory = DevFactory()
    mccs_master_leaf_node_device = dev_factory.get_device(
        HELPER_MCCS_MASTER_LEAF_NODE_DEVICE
    )
    defect = {
        "enabled": True,
        "fault_type": FaultType.COMMAND_NOT_ALLOWED,
        "error_message": "Device is stuck in Resourcing state",
        "result": ResultCode.FAILED,
    }
    mccs_master_leaf_node_device.SetDefective(json.dumps(defect))
    with pytest.raises(DevFailed):
        mccs_master_leaf_node_device.AssignResources("")

    mccs_master_leaf_node_device.SetDefective(json.dumps({"enabled": False}))
