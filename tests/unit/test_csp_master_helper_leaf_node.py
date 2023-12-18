import json

from ska_tango_base.commands import ResultCode

from ska_tmc_common import DevFactory
from tests.settings import HELPER_CSP_MASTER_LEAF_DEVICE


def test_csp_master_leaf_node_loadDishConfig_command(
    tango_context, json_factory
):
    """
    This test case invokes command on csp master Leaf device
    and checks whether the attributes are populated with
    relevant json data or not.
    """
    dev_factory = DevFactory()
    csp_master_leaf_device = dev_factory.get_device(
        HELPER_CSP_MASTER_LEAF_DEVICE
    )

    input_json_str = json_factory("mid_cbf_param_file uri")
    return_code, _ = csp_master_leaf_device.LoadDishCfg(input_json_str)

    assert return_code[0] == ResultCode.QUEUED
    assert csp_master_leaf_device.sourceDishVccConfig == input_json_str

    expected_json_str = json_factory("mid_cbf_initial_parameters")
    expected_json = json.loads(expected_json_str)
    dishVccConfig = json.loads(csp_master_leaf_device.dishVccConfig)

    # comparing dictionary instead of strings to avoid the issues with whitespaces
    assert expected_json == dishVccConfig
