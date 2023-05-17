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
    SubArrayAdapter,
)


@pytest.fixture(scope="module")
def devices_to_load():
    return (
        {
            "class": HelperSubArrayDevice,
            "devices": [{"name": "test/subarray/1"}],
        },
        {
            "class": HelperBaseDevice,
            "devices": [{"name": "test/base/1"}, {"name": "test/dish/1"}],
        },
        {
            "class": HelperMCCSStateDevice,
            "devices": [{"name": "test/mccs/1"}],
        },
        {
            "class": HelperCspMasterDevice,
            "devices": [{"name": "test/csp_master/1"}],
        },
    )


@pytest.mark.dd1
def test_get_or_create_base_adapter(tango_context):
    factory = AdapterFactory()
    base_adapter = factory.get_or_create_adapter(
        "test/base/1", AdapterType.BASE
    )
    assert isinstance(base_adapter, BaseAdapter)


@pytest.mark.dd1
def test_get_or_create_subarray_adapter(tango_context):
    factory = AdapterFactory()
    subarray_adapter = factory.get_or_create_adapter(
        "test/subarray/1", AdapterType.SUBARRAY
    )
    assert isinstance(subarray_adapter, SubArrayAdapter)


@pytest.mark.dd1
def test_get_or_create_dish_adapter(tango_context):
    factory = AdapterFactory()
    dish_adapter = factory.get_or_create_adapter(
        "test/dish/1", AdapterType.DISH
    )
    assert isinstance(dish_adapter, DishAdapter)


@pytest.mark.dd1
def test_get_or_create_mccs_adapter(tango_context):
    factory = AdapterFactory()
    mccs_adapter = factory.get_or_create_adapter(
        "test/mccs/1", AdapterType.MCCS
    )
    assert isinstance(mccs_adapter, MCCSAdapter)


@pytest.mark.dd1
def test_get_or_create_csp_adapter(tango_context):
    factory = AdapterFactory()
    csp_master_adapter = factory.get_or_create_adapter(
        "test/csp_master/1", AdapterType.CSPMASTER
    )
    assert isinstance(csp_master_adapter, CspMasterAdapter)
