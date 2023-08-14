import json

import pytest
from ska_tango_base.commands import ResultCode

from ska_tmc_common import DevFactory
from tests.settings import CSP_DEVICE

commands = ["On", "Off", "Standby"]


@pytest.mark.parametrize("command", commands)
def test_csp_commands(tango_context, command):
    dev_factory = DevFactory()
    csp_device = dev_factory.get_device(CSP_DEVICE)
    result, message = csp_device.command_inout(command, "")
    assert result[0] == ResultCode.OK
    assert message[0] == ""


@pytest.mark.parametrize("command", commands)
def test_csp_command_defective(tango_context, command):
    dev_factory = DevFactory()
    csp_device = dev_factory.get_device(CSP_DEVICE)
    csp_device.SetDefective(json.dumps({"enabled": True}))
    result, message = csp_device.command_inout(command, "")
    assert result[0] == ResultCode.FAILED
    assert message[0] == "Default exception."
