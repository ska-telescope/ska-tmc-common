import pytest

from ska_tmc_common.exceptions import (
    AdminModeException,
    ResourceReassignmentError,
)


def raise_exception():
    raise ResourceReassignmentError("Error occurred while assigning", "SKA001")


def raise_admin_mode_exception():
    raise AdminModeException("test_device", "On", "admin mode offline")


def test_exceptions():
    with pytest.raises(ResourceReassignmentError) as resource_exception:
        raise_exception()

    assert "Error occurred while assigning" == str(resource_exception.value)
    assert "SKA001" == resource_exception.value.resources_reallocation


def test_admin_mode_exceptions():
    with pytest.raises(AdminModeException) as admin_mode_exception:
        raise_admin_mode_exception()
    assert "test_device" == admin_mode_exception.value.device_name
    assert "On" == admin_mode_exception.value.command_name
    assert "admin mode offline" == admin_mode_exception.value.message
