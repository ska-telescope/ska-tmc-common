import pytest
from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.subarray import SKASubarray

from ska_tmc_common.adapters import (
    AdapterFactory,
    AdapterType,
    BaseAdapter,
    SubArrayAdapter,
)


@pytest.fixture(scope="module")
def devices_to_load():
    return (
        {
            "class": SKASubarray,
            "devices": [{"name": "test/device/1"}],
        },
        {
            "class": SKABaseDevice,
            "devices": [
                {"name": "test/device/2"},
            ],
        },
    )


def test_get_or_create_base_adapter(tango_context_multitest):
    factory = AdapterFactory()
    base_adapter = factory.get_or_create_adapter(
        "test/device/2", AdapterType.BASE
    )
    assert isinstance(base_adapter, BaseAdapter)


def test_get_or_create_subarray_adapter(tango_context_multitest):
    factory = AdapterFactory()
    subarray_adapter = factory.get_or_create_adapter(
        "test/device/1", AdapterType.SUBARRAY
    )
    assert isinstance(subarray_adapter, SubArrayAdapter)
