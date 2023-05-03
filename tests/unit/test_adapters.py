import pytest

from ska_tmc_common import (
    AdapterFactory,
    AdapterType,
    BaseAdapter,
    DishAdapter,
    HelperBaseDevice,
    HelperSubArrayDevice,
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
    )


def test_get_or_create_base_adapter(tango_context):
    factory = AdapterFactory()
    base_adapter = factory.get_or_create_adapter(
        "test/base/1", AdapterType.BASE
    )
    assert isinstance(base_adapter, BaseAdapter)


def test_get_or_create_subarray_adapter(tango_context):
    factory = AdapterFactory()
    subarray_adapter = factory.get_or_create_adapter(
        "test/subarray/1", AdapterType.SUBARRAY
    )
    assert isinstance(subarray_adapter, SubArrayAdapter)


def test_get_or_create_dish_adapter(tango_context):
    factory = AdapterFactory()
    dish_adapter = factory.get_or_create_adapter(
        "test/dish/1", AdapterType.DISH
    )
    assert isinstance(dish_adapter, DishAdapter)
