import pytest

from ska_tmc_common import (
    AdapterFactory,
    AdapterType,
    BaseAdapter,
    CspMasterAdapter,
    DishAdapter,
    HelperBaseDevice,
    HelperCspMasterDevice,
    HelperMCCSStateDevice,
    HelperSubArrayDevice,
    MCCSAdapter,
    SdpSubArrayAdapter,
    SdpSubarrayDevice,
    SubArrayAdapter,
)
from tests.settings import (
    HELPER_BASE_DEVICE,
    HELPER_CSP_MASTER_DEVICE,
    HELPER_DISH_DEVICE,
    HELPER_MCCS_STATE_DEVICE,
    HELPER_SDP_SUBARRAY_DEVICE,
    HELPER_SUBARRAY_DEVICE,
)


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
            "class": HelperMCCSStateDevice,
            "devices": [{"name": HELPER_MCCS_STATE_DEVICE}],
        },
        {
            "class": HelperCspMasterDevice,
            "devices": [{"name": HELPER_CSP_MASTER_DEVICE}],
        },
        {
            "class": SdpSubarrayDevice,
            "devices": [{"name": HELPER_SDP_SUBARRAY_DEVICE}],
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
    assert isinstance(subarray_adapter, SubArrayAdapter)


def test_get_or_create_dish_adapter(tango_context):
    factory = AdapterFactory()
    dish_adapter = factory.get_or_create_adapter(
        HELPER_DISH_DEVICE, AdapterType.DISH
    )
    assert isinstance(dish_adapter, DishAdapter)


def test_get_or_create_mccs_adapter(tango_context):
    factory = AdapterFactory()
    mccs_adapter = factory.get_or_create_adapter(
        HELPER_MCCS_STATE_DEVICE, AdapterType.MCCS
    )
    assert isinstance(mccs_adapter, MCCSAdapter)


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
