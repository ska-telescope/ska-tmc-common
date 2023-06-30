import json

import pytest
from ska_tango_base.commands import ResultCode

from ska_tmc_common import DevFactory, FaultType
from tests.settings import SUBARRAY_LEAF_DEVICE

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
def test_assign_resources(tango_context, command):
    dev_factory = DevFactory()
    subarray_leaf_device = dev_factory.get_device(SUBARRAY_LEAF_DEVICE)
    result, message = subarray_leaf_device.command_inout(command, "")
    assert result[0] == ResultCode.OK
    assert message[0] == ""


@pytest.mark.parametrize("command", commands_without_argin)
def test_command_without_argin(tango_context, command):
    dev_factory = DevFactory()
    subarray_leaf_device = dev_factory.get_device(SUBARRAY_LEAF_DEVICE)
    result, message = subarray_leaf_device.command_inout(command)
    assert result[0] == ResultCode.OK
    assert message[0] == ""


def test_assign_resources_defective(tango_context):
    dev_factory = DevFactory()
    subarray_leaf_device = dev_factory.get_device(SUBARRAY_LEAF_DEVICE)
    defect = {
        "value": False,
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
