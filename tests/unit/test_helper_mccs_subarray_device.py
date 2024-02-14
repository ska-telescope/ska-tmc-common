import pytest
from ska_tango_base.commands import ResultCode

from ska_tmc_common import DevFactory
from tests.settings import HELPER_MCCS_SUBARRAY_DEVICE

commands_with_argin = [
    "AssignResources",
    "Scan",
    "Configure",
]
commands_without_argin = [
    "ReleaseAllResources",
    "EndScan",
    "Restart",
    "End",
]


@pytest.mark.parametrize("command", commands_with_argin)
def test_mccs_subarray_device_commands_with_argument(tango_context, command):
    dev_factory = DevFactory()
    mccs_subarray_device = dev_factory.get_device(HELPER_MCCS_SUBARRAY_DEVICE)
    result, message = mccs_subarray_device.command_inout(command, "")
    assert result[0] == ResultCode.OK


@pytest.mark.parametrize("command", commands_without_argin)
def test_mccs_subarray_device_command_without_argin(tango_context, command):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(HELPER_MCCS_SUBARRAY_DEVICE)
    result, message = subarray_device.command_inout(command)
    assert result[0] == ResultCode.OK
