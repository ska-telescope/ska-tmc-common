from ska_tango_base.commands import ResultCode

from ska_tmc_common import DevFactory
from tests.settings import HELPER_MCCS_SUBARRAY_LEAF_NODE_DEVICE


def test_restart_subarray_command(tango_context):
    dev_factory = DevFactory()
    mccs_sln_device = dev_factory.get_device(
        HELPER_MCCS_SUBARRAY_LEAF_NODE_DEVICE
    )
    subarray_id = 1  # Provide the subarray ID as an argument to the RestartSubarray command
    result = mccs_sln_device.command_inout("Restart", subarray_id)
    assert result[0] == ResultCode.OK
