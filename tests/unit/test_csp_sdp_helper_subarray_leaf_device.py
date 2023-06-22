from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState

from ska_tmc_common import DevFactory
from tests.settings import CSP_LEAF_NODE_DEVICE, SDP_LEAF_NODE_DEVICE


def test_assign_resources_defective(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(
        CSP_LEAF_NODE_DEVICE, SDP_LEAF_NODE_DEVICE
    )
    subarray_device.SetDefective(True)
    result, message = subarray_device.AssignResources("")
    assert result[0] == ResultCode.FAILED
    assert (
        message[0] == "Device is Defective, cannot process command completely."
    )
    assert subarray_device.cspSubarrayObsState == ObsState.RESOURCING
    assert subarray_device.sdpSubarrayObsState == ObsState.RESOURCING
