import pytest
from ska_tango_base.commands import ResultCode

from ska_tmc_common import DevFactory
from tests.settings import HELPER_MCCS_MASTER_LEAF_NODE_DEVICE

commands = ["On", "Off", "AssignResources", "ReleaseResources"]


@pytest.mark.parametrize("command", commands)
def test_mccs_master_leaf_node_commands(tango_context, command):
    dev_factory = DevFactory()
    mccs_device = dev_factory.get_device(HELPER_MCCS_MASTER_LEAF_NODE_DEVICE)
    result, message = mccs_device.command_inout(command, "")
    assert result[0] == ResultCode.OK
    assert message[0] == ""
