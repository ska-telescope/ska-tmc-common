import json

import pytest
from ska_tango_base.commands import ResultCode

from ska_tmc_common import DevFactory
from tests.settings import CSP_DEVICE, DEFAULT_DEFECT_SETTINGS

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
    csp_device.SetDefective(json.dumps(DEFAULT_DEFECT_SETTINGS))
    result, message = csp_device.command_inout(command, "")
    assert result[0] == ResultCode.FAILED
    assert message[0] == "Default exception."


def test_csp_loadDishConfig_command(tango_context, json_factory):
    """
    This test case invokes command on csp master device
    and checks whether the attributes are populated with
    relevant json data or not.
    """
    dev_factory = DevFactory()
    csp_master_device = dev_factory.get_device(CSP_DEVICE)

    input_json_str = json_factory("mid_cbf_param_file uri")
    return_code, _ = csp_master_device.LoadDishCfg(input_json_str)

    assert return_code[0] == ResultCode.QUEUED
    assert csp_master_device.sourceDishVccConfig == input_json_str

    expected_json_str = json_factory("mid_cbf_initial_parameters")
    expected_json = json.loads(expected_json_str)
    dishVccConfig = json.loads(csp_master_device.dishVccConfig)

    # comparing dictionary instead of strings
    # to avoid the issues with whitespaces
    assert expected_json == dishVccConfig
