import json
import logging

import mock
import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import AdminMode
from tango import DevState

from ska_tmc_common import (
    AdapterFactory,
    AdapterType,
    BaseAdapter,
    CspMasterAdapter,
    DishAdapter,
    DishLeafAdapter,
    EmptySubArrayComponentManager,
    HelperBaseDevice,
    HelperCspMasterDevice,
    HelperCspMasterLeafDevice,
    HelperMCCSController,
    HelperMCCSMasterLeafNode,
    HelperSdpSubarray,
    HelperSubArrayDevice,
    MCCSControllerAdapter,
    MCCSMasterLeafNodeAdapter,
    SdpSubArrayAdapter,
    SubarrayAdapter,
    TmcLeafNodeCommand,
)
from tests.settings import (
    HELPER_BASE_DEVICE,
    HELPER_CSP_MASTER_DEVICE,
    HELPER_CSP_MASTER_LEAF_DEVICE,
    HELPER_DISH_DEVICE,
    HELPER_MCCS_CONTROLLER,
    HELPER_MCCS_MASTER_LEAF_NODE_DEVICE,
    HELPER_SDP_SUBARRAY_DEVICE,
    HELPER_SUBARRAY_DEVICE,
    MCCS_SUBARRAY_LEAF_NODE,
)

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def devices_to_load():
    return (
        {
            "class": HelperSubArrayDevice,
            "devices": [
                {"name": HELPER_SUBARRAY_DEVICE},
                {"name": MCCS_SUBARRAY_LEAF_NODE},
            ],
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
            "class": HelperCspMasterLeafDevice,
            "devices": [{"name": HELPER_CSP_MASTER_LEAF_DEVICE}],
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


def test_base_adapter(tango_context):
    factory = AdapterFactory()

    subarray_adapter = factory.get_or_create_adapter(
        HELPER_SUBARRAY_DEVICE, AdapterType.SUBARRAY
    )

    assert subarray_adapter.proxy is not None
    subarray_adapter.adminMode = AdminMode.ONLINE
    result_code, unique_id = subarray_adapter.On()
    assert result_code == ResultCode.QUEUED
    assert unique_id[0].endswith("On")

    result_code, unique_id = subarray_adapter.Off()
    assert result_code == ResultCode.QUEUED
    assert unique_id[0].endswith("Off")

    result_code, unique_id = subarray_adapter.Standby()
    assert result_code == ResultCode.QUEUED
    assert unique_id[0].endswith("Standby")
    assert subarray_adapter.State() in [
        DevState.DISABLE,
        DevState.UNKNOWN,
        DevState.OFF,
        DevState.STANDBY,
        DevState.ON,
    ]

    # Mocking behaviour as this commands are not implemented
    subarray_adapter._proxy = mock.Mock()
    attrs = {
        "Disable.return_value": (ResultCode.OK, ["Command Completed"]),
        "Reset.return_value": (ResultCode.OK, ["Command Completed"]),
    }
    subarray_adapter._proxy.configure_mock(**attrs)
    result_code, message = subarray_adapter.Disable()
    assert result_code == ResultCode.OK
    result_code, message = subarray_adapter.Reset()
    assert result_code == ResultCode.OK


def test_get_or_create_dish_adapter(tango_context):
    factory = AdapterFactory()
    dish_adapter = factory.get_or_create_adapter(
        HELPER_DISH_DEVICE, AdapterType.DISH
    )
    assert isinstance(dish_adapter, DishAdapter)


def test_get_or_create_dish_leaf_node_adapter(tango_context):
    factory = AdapterFactory()
    dish_adapter = factory.get_or_create_adapter(
        HELPER_DISH_DEVICE, AdapterType.DISH_LEAF_NODE
    )
    assert isinstance(dish_adapter, DishLeafAdapter)


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


def test_csp_master_leaf_node_memorized_dish_vcc_attribute(tango_context):
    """Validate dish vcc map memorized attribute set using adapter"""
    factory = AdapterFactory()
    csp_master_leaf_node_adapter = factory.get_or_create_adapter(
        HELPER_CSP_MASTER_LEAF_DEVICE, AdapterType.CSP_MASTER_LEAF_NODE
    )
    assert csp_master_leaf_node_adapter.memorizedDishVccMap == ""

    csp_master_leaf_node_adapter.memorizedDishVccMap = json.dumps(
        {"uri": "dummy_url"}
    )

    assert csp_master_leaf_node_adapter.memorizedDishVccMap == json.dumps(
        {"uri": "dummy_url"}
    )


def test_csp_master_leaf_node(tango_context):
    """Validate dish vcc map memorized attribute set using adapter"""
    factory = AdapterFactory()
    csp_master_leaf_node_adapter = factory.get_or_create_adapter(
        HELPER_CSP_MASTER_LEAF_DEVICE, AdapterType.CSP_MASTER_LEAF_NODE
    )
    attrs = {
        "LoadDishCfg.return_value": (ResultCode.OK, ["Command Completed"])
    }
    csp_master_leaf_node_adapter._proxy = mock.Mock()
    csp_master_leaf_node_adapter._proxy.configure_mock(**attrs)
    return_code, _ = csp_master_leaf_node_adapter.LoadDishCfg("")
    assert return_code == ResultCode.OK


def test_dish_adapter_program_track_table(tango_context):
    """Test program_track_table property on dish adapter"""
    factory = AdapterFactory()
    dish_adapter = factory.get_or_create_adapter(
        HELPER_DISH_DEVICE, AdapterType.DISH
    )
    dish_adapter.program_track_table = [
        1706629796036.8691,
        181.223951890779,
        31.189377349638,
    ]
    assert dish_adapter.program_track_table == [
        1706629796036.8691,
        181.223951890779,
        31.189377349638,
    ]


def test_get_or_create_mccs_subarray_leaf_node_adapter(tango_context):
    factory = AdapterFactory()
    mccs_subarray_leaf_node_adapter = factory.get_or_create_adapter(
        MCCS_SUBARRAY_LEAF_NODE,
        AdapterType.SUBARRAY,
    )
    assert isinstance(mccs_subarray_leaf_node_adapter, SubarrayAdapter)


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


def test_call_adapter_method(tango_context):
    factory = AdapterFactory()
    subarray_adapter = factory.get_or_create_adapter(
        HELPER_SUBARRAY_DEVICE, AdapterType.SUBARRAY
    )
    subarray_adapter.adminMode = AdminMode.ONLINE
    tmc_leaf_node_command_obj = TmcLeafNodeCommand(
        EmptySubArrayComponentManager(
            logger=logger,
            communication_state_callback=None,
            component_state_callback=None,
        ),
        logger,
    )
    result_code, command_id = tmc_leaf_node_command_obj.call_adapter_method(
        HELPER_SDP_SUBARRAY_DEVICE, subarray_adapter, "AssignResources", ""
    )
    assert result_code[0] == ResultCode.QUEUED
    assert "AssignResources" in command_id[0]


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
        + "The following exception occurred - "
        + "SubarrayAdapter.AssignResources() "
        + "missing 1 required positional argument: 'argin'."
    )
