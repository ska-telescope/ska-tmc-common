import logging

import pytest
from ska_tango_base.commands import ResultCode

from ska_tmc_common import (
    AdapterFactory,
    AdapterType,
    BaseAdapter,
    CspMasterAdapter,
    CspSubarrayAdapter,
    DishAdapter,
    HelperBaseDevice,
    HelperCspMasterDevice,
    HelperMCCSController,
    HelperMCCSMasterLeafNode,
    HelperSubArrayDevice,
    MCCSControllerAdapter,
    MCCSMasterLeafNodeAdapter,
    SdpSubArrayAdapter,
    SubarrayAdapter,
    TmcLeafNodeCommand,
)
from ska_tmc_common.test_helpers.helper_csp_subarray import HelperCspSubarray
from ska_tmc_common.test_helpers.helper_sdp_subarray import HelperSdpSubarray
from ska_tmc_common.test_helpers.helper_subarray_device import (
    EmptySubArrayComponentManager,
)
from tests.settings import (
    HELPER_BASE_DEVICE,
    HELPER_CSP_MASTER_DEVICE,
    HELPER_CSP_SUBARRAY_DEVICE,
    HELPER_DISH_DEVICE,
    HELPER_MCCS_CONTROLLER,
    HELPER_MCCS_MASTER_LEAF_NODE_DEVICE,
    HELPER_SDP_SUBARRAY_DEVICE,
    HELPER_SUBARRAY_DEVICE,
)

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def devices_to_load():
    return (
        {
            "class": HelperSubArrayDevice,
            "devices": [{"name": HELPER_SUBARRAY_DEVICE}],
        },
        {
            "class": HelperBaseDevice,
            "devices": [
                {"name": HELPER_BASE_DEVICE},
                {"name": HELPER_DISH_DEVICE},
            ],
        },
        {
            "class": HelperMCCSController,
            "devices": [{"name": HELPER_MCCS_CONTROLLER}],
        },
        {
            "class": HelperMCCSMasterLeafNode,
            "devices": [{"name": HELPER_MCCS_MASTER_LEAF_NODE_DEVICE}],
        },
        {
            "class": HelperCspMasterDevice,
            "devices": [{"name": HELPER_CSP_MASTER_DEVICE}],
        },
        {
            "class": HelperSdpSubarray,
            "devices": [{"name": HELPER_SDP_SUBARRAY_DEVICE}],
        },
        {
            "class": HelperCspSubarray,
            "devices": [{"name": HELPER_CSP_SUBARRAY_DEVICE}],
        },
    )


def test_get_or_create_base_adapter(tango_context):
    factory = AdapterFactory()
    base_adapter = factory.get_or_create_adapter(
        HELPER_BASE_DEVICE, AdapterType.BASE
    )
    assert isinstance(base_adapter, BaseAdapter)


def test_get_or_create_subarray_adapter(tango_context):
    factory = AdapterFactory()
    subarray_adapter = factory.get_or_create_adapter(
        HELPER_SUBARRAY_DEVICE, AdapterType.SUBARRAY
    )
    assert isinstance(subarray_adapter, SubarrayAdapter)


def test_get_or_create_dish_adapter(tango_context):
    factory = AdapterFactory()
    dish_adapter = factory.get_or_create_adapter(
        HELPER_DISH_DEVICE, AdapterType.DISH
    )
    assert isinstance(dish_adapter, DishAdapter)


def test_get_or_create_mccs_controller_adapter(tango_context):
    factory = AdapterFactory()
    mccs_adapter = factory.get_or_create_adapter(
        HELPER_MCCS_CONTROLLER, AdapterType.MCCS_CONTROLLER
    )
    assert isinstance(mccs_adapter, MCCSControllerAdapter)


def test_get_or_create_mccs_master_leaf_node_adapter(tango_context):
    factory = AdapterFactory()
    mccs_master_leaf_node_adapter = factory.get_or_create_adapter(
        HELPER_MCCS_MASTER_LEAF_NODE_DEVICE, AdapterType.MCCS_MASTER_LEAF_NODE
    )
    assert isinstance(mccs_master_leaf_node_adapter, MCCSMasterLeafNodeAdapter)


def test_get_or_create_csp_adapter(tango_context):
    factory = AdapterFactory()
    csp_master_adapter = factory.get_or_create_adapter(
        HELPER_CSP_MASTER_DEVICE, AdapterType.CSPMASTER
    )
    assert isinstance(csp_master_adapter, CspMasterAdapter)


def test_get_or_create_sdp_adapter(tango_context):
    factory = AdapterFactory()
    sdp_subarray_adapter = factory.get_or_create_adapter(
        HELPER_SDP_SUBARRAY_DEVICE, AdapterType.SDPSUBARRAY
    )
    assert isinstance(sdp_subarray_adapter, SdpSubArrayAdapter)


def test_get_or_create_csp_subarray_adapter(tango_context):
    factory = AdapterFactory()
    csp_subarray_adapter = factory.get_or_create_adapter(
        HELPER_CSP_SUBARRAY_DEVICE, AdapterType.CSPSUBARRAY
    )
    assert isinstance(csp_subarray_adapter, CspSubarrayAdapter)


def test_call_adapter_method(tango_context):
    factory = AdapterFactory()
    subarray_adapter = factory.get_or_create_adapter(
        HELPER_SUBARRAY_DEVICE, AdapterType.SUBARRAY
    )
    tmc_leaf_node_command_obj = TmcLeafNodeCommand(
        EmptySubArrayComponentManager(
            logger=logger,
            communication_state_callback=None,
            component_state_callback=None,
        ),
        logger,
    )
    result_code, message = tmc_leaf_node_command_obj.call_adapter_method(
        HELPER_SDP_SUBARRAY_DEVICE, subarray_adapter, "AssignResources", ""
    )
    assert result_code[0] == ResultCode.OK
    assert message[0] == ""


def test_call_adapter_method_exception(tango_context):
    factory = AdapterFactory()
    subarray_adapter = factory.get_or_create_adapter(
        HELPER_SUBARRAY_DEVICE, AdapterType.SUBARRAY
    )
    tmc_leaf_node_command_obj = TmcLeafNodeCommand(
        EmptySubArrayComponentManager(
            logger=logger,
            communication_state_callback=None,
            component_state_callback=None,
        ),
        logger,
    )
    result_code, message = tmc_leaf_node_command_obj.call_adapter_method(
        HELPER_SUBARRAY_DEVICE, subarray_adapter, "AssignResources"
    )
    assert result_code[0] == ResultCode.FAILED
    assert (
        message[0]
        == "The invocation of the AssignResources command is failed on "
        + "test/subarray/1 device test/subarray/1.\n"
        + "The following exception occurred - SubArrayAdapter.AssignResources() "
        + "missing 1 required positional argument: 'argin'."
    )
