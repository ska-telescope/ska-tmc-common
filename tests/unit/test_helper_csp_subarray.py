import json

import pytest
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode

from ska_tmc_common import DevFactory
from ska_tmc_common.test_helpers.helper_csp_subarray import HelperCspSubarray
from tests.settings import CSP_SUBARRAY_DEVICE, DEFAULT_DEFECT_SETTINGS


@pytest.fixture(scope="module")
def devices_to_load():
    return (
        {
            "class": HelperCspSubarray,
            "devices": [{"name": CSP_SUBARRAY_DEVICE}],
        },
    )


commands_with_argin = ["AssignResources", "Configure", "Scan"]
commands_without_argin = [
    "On",
    "Off",
    "ReleaseAllResources",
    "EndScan",
    "ObsReset",
    "Restart",
    "Standby",
    "GoToIdle",
    "Abort",
    "Restart",
    "GoToIdle",
    "ReleaseResources",
]


def test_set_delay(tango_context):
    dev_factory = DevFactory()
    csp_subarray_device = dev_factory.get_device(CSP_SUBARRAY_DEVICE)
    csp_subarray_device.SetDelay('{"Configure": 3}')
    command_delay_info = json.loads(csp_subarray_device.commandDelayInfo)
    assert command_delay_info["Configure"] == 3


def test_set_defective(tango_context):
    dev_factory = DevFactory()
    csp_subarray_device = dev_factory.get_device(CSP_SUBARRAY_DEVICE)
    csp_subarray_device.SetDefective(json.dumps(DEFAULT_DEFECT_SETTINGS))
    result, command_id = csp_subarray_device.AssignResources("")
    assert result[0] == ResultCode.FAILED
    assert "AssignResources" in command_id[0]
    csp_subarray_device.SetDefective(json.dumps({"enabled": False}))


def test_set_raise_exception(tango_context):
    dev_factory = DevFactory()
    csp_subarray_device = dev_factory.get_device(CSP_SUBARRAY_DEVICE)
    assert not csp_subarray_device.raiseException
    csp_subarray_device.SetRaiseException(True)
    assert csp_subarray_device.raiseException


@pytest.mark.parametrize("command", commands_with_argin)
def test_command_with_argin(tango_context, command):
    dev_factory = DevFactory()
    csp_subarray_device = dev_factory.get_device(CSP_SUBARRAY_DEVICE)
    result, command_id = csp_subarray_device.command_inout(command, "")
    assert result[0] == ResultCode.QUEUED
    assert isinstance(command_id[0], str)


@pytest.mark.parametrize("command", commands_without_argin)
def test_command_without_argin(tango_context, command):
    dev_factory = DevFactory()
    csp_subarray_device = dev_factory.get_device(CSP_SUBARRAY_DEVICE)
    result, command_id = csp_subarray_device.command_inout(command)
    assert result[0] == ResultCode.QUEUED
    assert isinstance(command_id[0], str)


def test_assign_resources_defective(tango_context):
    dev_factory = DevFactory()
    csp_subarray_device = dev_factory.get_device(CSP_SUBARRAY_DEVICE)
    csp_subarray_device.SetDefective(json.dumps(DEFAULT_DEFECT_SETTINGS))
    result, command_id = csp_subarray_device.AssignResources("")
    assert result[0] == ResultCode.FAILED
    assert "AssignResources" in command_id[0]
    csp_subarray_device.SetDefective(json.dumps({"enabled": False}))


def test_scan_command(tango_context):
    dev_factory = DevFactory()
    csp_subarray_device = dev_factory.get_device(CSP_SUBARRAY_DEVICE)
    result, command_id = csp_subarray_device.Scan("")
    assert result[0] == ResultCode.QUEUED
    assert csp_subarray_device.obsstate == ObsState.SCANNING
    assert isinstance(command_id[0], str)


def test_release_resources_defective(tango_context):
    dev_factory = DevFactory()
    csp_subarray_device = dev_factory.get_device(CSP_SUBARRAY_DEVICE)
    csp_subarray_device.SetDefective(json.dumps(DEFAULT_DEFECT_SETTINGS))
    result, command_id = csp_subarray_device.ReleaseAllResources()
    assert result[0] == ResultCode.FAILED
    assert "ReleaseAllResources" in command_id[0]
    csp_subarray_device.SetDefective(json.dumps({"enabled": False}))


def test_assign_resources_raise_exception(tango_context):
    dev_factory = DevFactory()
    csp_subarray_device = dev_factory.get_device(CSP_SUBARRAY_DEVICE)
    csp_subarray_device.SetRaiseException(True)
    result, message = csp_subarray_device.AssignResources("")
    assert result[0] == ResultCode.QUEUED
    assert csp_subarray_device.obsstate == ObsState.RESOURCING


def test_release_resources_raise_exception(tango_context):
    dev_factory = DevFactory()
    csp_subarray_device = dev_factory.get_device(CSP_SUBARRAY_DEVICE)
    csp_subarray_device.SetRaiseException(True)
    result, message = csp_subarray_device.ReleaseAllResources()
    assert result[0] == ResultCode.QUEUED
    assert csp_subarray_device.obsstate == ObsState.RESOURCING
