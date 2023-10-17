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


@pytest.mark.dish
def test_csp_loaddishconfig(tango_context, json_factory):
    dev_factory = DevFactory()
    csp_master_device = dev_factory.get_device(CSP_DEVICE)
    input_json_str = json_factory("mid_cbf_param_file uri")
    return_code, _ = csp_master_device.LoadDishCfg(input_json_str)
    assert return_code == ResultCode.OK
    assert csp_master_device.sourceSysParam == input_json_str
    layout_json = json_factory("mid-layout")
    assert csp_master_device.sysParam == layout_json
