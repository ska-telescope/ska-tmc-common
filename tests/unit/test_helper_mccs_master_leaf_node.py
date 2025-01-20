import json

import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import AdminMode
from tango import DevFailed

from ska_tmc_common import DevFactory, FaultType
from tests.settings import (
    FAILED_RESULT_DEFECT,
    FAILED_RESULT_DEFECT_EXCEPTION,
    HELPER_MCCS_MASTER_LEAF_NODE_DEVICE,
)

commands_with_argin = ["AssignResources", "ReleaseAllResources"]
commands_without_argin = ["On", "Off"]


@pytest.mark.parametrize("command", commands_with_argin)
def test_mccs_master_leaf_node_commands_with_argument(tango_context, command):
    dev_factory = DevFactory()
    mccs_master_leaf_node_device = dev_factory.get_device(
        HELPER_MCCS_MASTER_LEAF_NODE_DEVICE
    )
    mccs_master_leaf_node_device.adminMode = AdminMode.ONLINE
    result, message = mccs_master_leaf_node_device.command_inout(command, "")
    assert result[0] == ResultCode.QUEUED


@pytest.mark.parametrize("command", commands_without_argin)
def test_mccs_master_leaf_node_commands_without_argument(
    tango_context, command
):
    dev_factory = DevFactory()
    mccs_master_leaf_node_device = dev_factory.get_device(
        HELPER_MCCS_MASTER_LEAF_NODE_DEVICE
    )
    mccs_master_leaf_node_device.adminMode = AdminMode.ONLINE
    result, command_id = mccs_master_leaf_node_device.command_inout(command)
    assert result[0] == ResultCode.QUEUED
    assert isinstance(command_id[0], str)


def test_assign_resources_failed_result(tango_context):
    dev_factory = DevFactory()
    mccs_master_leaf_node_device = dev_factory.get_device(
        HELPER_MCCS_MASTER_LEAF_NODE_DEVICE
    )
    mccs_master_leaf_node_device.adminMode = AdminMode.ONLINE
    mccs_master_leaf_node_device.SetDefective(json.dumps(FAILED_RESULT_DEFECT))
    result, message = mccs_master_leaf_node_device.AssignResources("")
    assert result[0] == ResultCode.FAILED
    assert FAILED_RESULT_DEFECT_EXCEPTION in message[0]
    mccs_master_leaf_node_device.SetDefective(json.dumps({"enabled": False}))


def test_assign_resources_command_not_allowed(tango_context):
    dev_factory = DevFactory()
    mccs_master_leaf_node_device = dev_factory.get_device(
        HELPER_MCCS_MASTER_LEAF_NODE_DEVICE
    )
    defect = {
        "enabled": True,
        "fault_type": FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING,
        "error_message": "Device is stuck in Resourcing state",
        "result": ResultCode.FAILED,
    }
    mccs_master_leaf_node_device.adminMode = AdminMode.ONLINE
    mccs_master_leaf_node_device.SetDefective(json.dumps(defect))
    with pytest.raises(DevFailed):
        mccs_master_leaf_node_device.AssignResources("")

    mccs_master_leaf_node_device.SetDefective(json.dumps({"enabled": False}))
