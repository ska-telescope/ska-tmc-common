"""Test Admin mode command for offline and online admin mode"""

import pytest
import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import AdminMode

from ska_tmc_common import (
    AdapterFactory,
    AdapterType,
    DevFactory,
    HelperCspMasterDevice,
    HelperCspMasterLeafDevice,
    HelperSubArrayDevice,
)
from tests.settings import (
    CSP_DEVICE,
    CSP_SUBARRAY_DEVICE_LOW,
    CSP_SUBARRAY_DEVICE_MID,
    HELPER_CSP_MASTER_LEAF_DEVICE,
    HELPER_SUBARRAY_DEVICE,
)


@pytest.fixture(scope="module")
def devices_to_load():
    return (
        {
            "class": HelperSubArrayDevice,
            "devices": [
                {"name": HELPER_SUBARRAY_DEVICE},
                {"name": CSP_SUBARRAY_DEVICE_LOW},
                {"name": CSP_SUBARRAY_DEVICE_MID},
            ],
        },
        {
            "class": HelperCspMasterLeafDevice,
            "devices": [
                {"name": HELPER_CSP_MASTER_LEAF_DEVICE},
            ],
        },
        {
            "class": HelperCspMasterDevice,
            "devices": [
                {"name": CSP_DEVICE},
            ],
        },
    )


def test_admin_mode_default_admin_mode(tango_context):
    """test invocation with admin mode online"""
    factory = AdapterFactory()

    subarray_adapter = factory.get_or_create_adapter(
        HELPER_SUBARRAY_DEVICE, AdapterType.SUBARRAY
    )
    assert subarray_adapter.proxy.adminMode == AdminMode.OFFLINE


def test_admin_mode_offline(tango_context):
    """test invocation with admin mode offline"""
    factory = AdapterFactory()

    subarray_adapter = factory.get_or_create_adapter(
        HELPER_SUBARRAY_DEVICE, AdapterType.SUBARRAY
    )
    subarray_adapter.proxy.adminMode = AdminMode.OFFLINE
    with pytest.raises(tango.DevFailed) as exc_info:
        subarray_adapter.On()
    assert "Command On not allowed" in str(exc_info)


def test_admin_mode_engineering(tango_context):
    """test invocation with admin mode Engineering"""
    factory = AdapterFactory()

    subarray_adapter = factory.get_or_create_adapter(
        HELPER_SUBARRAY_DEVICE, AdapterType.SUBARRAY
    )
    subarray_adapter.proxy.adminMode = AdminMode.ENGINEERING
    with pytest.raises(tango.DevFailed) as exc_info:
        subarray_adapter.On()
    assert "Command On not allowed" in str(exc_info)
    # Assert the exception message or any expected behavior


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


def test_csp_master_leaf_node_command_admin_mode_default(tango_context):
    """
    This test case validates if default admin mode of
    leafnode is
    """
    dev_factory = DevFactory()
    csp_master_leaf_device = dev_factory.get_device(
        HELPER_CSP_MASTER_LEAF_DEVICE
    )
    csp_master_leaf_device.On()
    assert csp_master_leaf_device.isAdminModeEnabled is not True


def test_csp_master_leaf_node_command_admin_mode_True(tango_context):
    """
    This test case validates if default admin mode of
    leafnode is
    """
    dev_factory = DevFactory()
    csp_master_leaf_device = dev_factory.get_device(
        HELPER_CSP_MASTER_LEAF_DEVICE
    )
    csp_master_leaf_device.isAdminModeEnabled = True
    with pytest.raises(tango.DevFailed) as exc_info:
        csp_master_leaf_device.On()
    assert "Command On not allowed" in str(exc_info)
    csp_master_leaf_device.adminMode = AdminMode.ONLINE
    csp_master_leaf_device.On()


def test_csp_master_leaf_node_feature_toggle(tango_context):
    """
    This test case validates if default admin mode of
    leafnode is
    """
    dev_factory = DevFactory()
    csp_master_leaf_device = dev_factory.get_device(
        HELPER_CSP_MASTER_LEAF_DEVICE
    )
    csp_master_leaf_device.isAdminModeEnabled = True
    with pytest.raises(tango.DevFailed) as exc_info:
        csp_master_leaf_device.On()
    assert "Command On not allowed" in str(exc_info)
    csp_master_leaf_device.isAdminModeEnabled = False
    csp_master_leaf_device.On()


def test_csp_device_default_admin_mode(tango_context):
    """
    This test case validates if default admin mode of
    leafnode is
    """
    dev_factory = DevFactory()
    csp_master_device = dev_factory.get_device(CSP_DEVICE)
    csp_subarray_device = dev_factory.get_device(HELPER_SUBARRAY_DEVICE)
    assert csp_master_device.adminMode == AdminMode.OFFLINE
    assert csp_subarray_device.adminMode == AdminMode.OFFLINE


def test_csp_device_admin_mode_mid(tango_context):
    """
    This test case validates if default admin mode of
    leafnode is
    """
    dev_factory = DevFactory()
    csp_master_device = dev_factory.get_device(CSP_DEVICE)
    csp_subarray_device_mid = dev_factory.get_device(CSP_SUBARRAY_DEVICE_MID)
    csp_subarray_device_low = dev_factory.get_device(CSP_SUBARRAY_DEVICE_LOW)
    assert csp_subarray_device_mid.adminMode == AdminMode.OFFLINE
    csp_master_device.adminMode = AdminMode.OFFLINE
    # changing csp master admin will also change subarray admin mode
    csp_master_device.adminMode = AdminMode.ONLINE
    assert csp_master_device.adminMode == AdminMode.ONLINE
    assert csp_subarray_device_mid.adminMode == AdminMode.ONLINE
    # check that only mid admin mode changes when mid is
    assert csp_subarray_device_low.adminMode == AdminMode.OFFLINE
