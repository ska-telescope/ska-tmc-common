import json

from ska_tango_base.commands import ResultCode

from ska_tmc_common import DevFactory, FaultType
from tests.settings import CSP_LEAF_NODE_DEVICE


def test_assign_resources_defective(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(CSP_LEAF_NODE_DEVICE)
    defect = {
        "enabled": True,
        "fault_type": FaultType.FAILED_RESULT,
        "error_message": (
            "Device is defective, cannot process command." "completely."
        ),
        "result": ResultCode.FAILED,
    }
    subarray_device.SetDefective(json.dumps(defect))
    result, command_id = subarray_device.AssignResources("")
    assert result[0] == ResultCode.FAILED
    assert "AssignResources" in command_id[0]
    subarray_device.SetDefective(json.dumps({"enabled": False}))
