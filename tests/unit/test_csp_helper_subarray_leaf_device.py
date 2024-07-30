import json

from ska_tango_base.commands import ResultCode

from ska_tmc_common import DevFactory
from tests.settings import (
    CSP_LEAF_NODE_DEVICE,
    FAILED_RESULT_DEFECT,
    FAILED_RESULT_DEFECT_EXCEPTION,
)


def test_assign_resources_defective(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(CSP_LEAF_NODE_DEVICE)
    subarray_device.SetDefective(json.dumps(FAILED_RESULT_DEFECT))
    result, command_id = subarray_device.AssignResources("")
    assert result[0] == ResultCode.FAILED
    assert FAILED_RESULT_DEFECT_EXCEPTION in command_id[0]
    subarray_device.SetDefective(json.dumps({"enabled": False}))
