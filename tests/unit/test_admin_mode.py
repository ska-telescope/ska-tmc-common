"""Test Admin mode command for offline and online admin mode"""

import os

import pytest
import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import AdminMode

from ska_tmc_common import AdapterFactory, AdapterType, HelperSubArrayDevice
from tests.settings import HELPER_SUBARRAY_DEVICE


@pytest.fixture(scope="module")
def devices_to_load():
    return (
        {
            "class": HelperSubArrayDevice,
            "devices": [
                {"name": HELPER_SUBARRAY_DEVICE},
            ],
        },
    )


def test_admin_mode_offline(tango_context):
    """test invocation with admin mode offline"""
    factory = AdapterFactory()

    subarray_adapter = factory.get_or_create_adapter(
        HELPER_SUBARRAY_DEVICE, AdapterType.SUBARRAY
    )

    assert subarray_adapter.proxy is not None
    with pytest.raises(tango.DevFailed) as exc_info:
        subarray_adapter.On()
    # Assert the exception message or any expected behavior
    assert "Device: HelperSubArrayDevice is in OFFLINE adminMode" in (
        str(exc_info.value)
    )
    assert "ska_tmc_common.exceptions.AdminModeException" in (
        str(exc_info.value)
    )


def test_admin_mode_engineering(tango_context):
    """test invocation with admin mode Engineering"""
    factory = AdapterFactory()

    subarray_adapter = factory.get_or_create_adapter(
        HELPER_SUBARRAY_DEVICE, AdapterType.SUBARRAY
    )
    subarray_adapter.proxy.adminMode = AdminMode.ENGINEERING
    assert subarray_adapter.proxy is not None
    with pytest.raises(tango.DevFailed) as exc_info:
        subarray_adapter.On()
    # Assert the exception message or any expected behavior
    assert "Device: HelperSubArrayDevice is in ENGINEERING adminMode" in (
        str(exc_info.value)
    )
    assert "ska_tmc_common.exceptions.AdminModeException" in (
        str(exc_info.value)
    )


def test_admin_mode_online(tango_context):
    """test invocation with admin mode online"""
    factory = AdapterFactory()

    subarray_adapter = factory.get_or_create_adapter(
        HELPER_SUBARRAY_DEVICE, AdapterType.SUBARRAY
    )
    subarray_adapter.proxy.adminMode = AdminMode.ONLINE
    assert subarray_adapter.proxy is not None
    result_code, unique_id = subarray_adapter.On()
    assert result_code == ResultCode.QUEUED
    assert unique_id[0].endswith("On")


def test_admin_mode_feature_toggle(tango_context):
    """Test invocation with admin mode offline."""
    factory = AdapterFactory()

    subarray_adapter = factory.get_or_create_adapter(
        HELPER_SUBARRAY_DEVICE, AdapterType.SUBARRAY
    )

    assert subarray_adapter.proxy is not None

    # Set environment variable to enable admin mode check
    os.environ["Admin_Mode_Feature"] = "true"

    with pytest.raises(tango.DevFailed) as exc_info:
        subarray_adapter.On()

    # Assert the exception message or any expected behavior
    assert "Device: HelperSubArrayDevice is in OFFLINE adminMode" in (
        str(exc_info.value)
    )
    assert "ska_tmc_common.exceptions.AdminModeException" in (
        str(exc_info.value)
    )

    # Now disable the Admin_Mode_Feature and test behavior
    os.environ["Admin_Mode_Feature"] = "false"

    try:
        subarray_adapter.On()
    except tango.DevFailed as e:
        pytest.fail(f"Unexpected DevFailed exception raised: {e}")

    # Reset the environment variable to avoid side effects
    del os.environ["Admin_Mode_Feature"]
