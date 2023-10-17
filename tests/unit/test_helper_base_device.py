import json

from ska_tango_base.commands import ResultCode

from ska_tmc_common import DevFactory
from tests.settings import CSP_LEAF_NODE_DEVICE, SDP_LEAF_NODE_DEVICE


def test_set_raise_exception_csp(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(CSP_LEAF_NODE_DEVICE)
    assert not subarray_device.raiseException
    subarray_device.SetRaiseException(True)
    assert subarray_device.raiseException


def test_set_raise_exception_sdp(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SDP_LEAF_NODE_DEVICE)
    assert not subarray_device.raiseException
    subarray_device.SetRaiseException(True)
    assert subarray_device.raiseException


def test_cspln_loadDishConfig_command(tango_context, json_factory):
    """
    This test case invokes command on csp master leaf node device
    and checks whether the attributes are populated with
    relevant json data or not.
    """
    dev_factory = DevFactory()
    csp_master_device = dev_factory.get_device(CSP_LEAF_NODE_DEVICE)

    input_json_str = json_factory("mid_cbf_param_file uri")
    return_code, _ = csp_master_device.LoadDishCfg(input_json_str)

    assert return_code == ResultCode.OK
    assert csp_master_device.sourceSysParam == input_json_str

    expected_json_str = json_factory("mid_cbf_initial_parameters")
    expected_json = json.loads(expected_json_str)
    sysParam = json.loads(csp_master_device.sysParam)

    # comparing dictionary instead of strings to avoid the issues with whitespaces
    assert expected_json == sysParam
