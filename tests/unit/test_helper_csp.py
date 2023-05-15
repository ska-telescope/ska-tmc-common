import pytest
from ska_tango_base.commands import ResultCode

from ska_tmc_common import DevFactory
from tests.settings import CSP_DEVICE

commands = ["On", "Off"]


@pytest.mark.dd
@pytest.mark.parametrize("command", commands)
def test_csp_commands(tango_context, command):
    dev_factory = DevFactory()
    csp_device = dev_factory.get_device(CSP_DEVICE)
    result, message = getattr(csp_device, command)("")
    assert result[0] == ResultCode.OK
    assert message[0] == ""


@pytest.mark.dd
@pytest.mark.parametrize("command", commands)
def test_csp_command_defective(tango_context, command):
    dev_factory = DevFactory()
    csp_device = dev_factory.get_device(CSP_DEVICE)
    csp_device.SetDefective(True)
    result, message = getattr(csp_device, command)("")
    assert result[0] == ResultCode.FAILED
    assert message[0] == "Device is Defective, cannot process command."
