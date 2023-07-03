import pytest
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode

from ska_tmc_common import DevFactory
from tests.settings import SUBARRAY_DEVICE

commands_with_argin = ["AssignResources", "Scan", "Configure", "Scan"]
commands_without_argin = [
    "On",
    "Off",
    "ReleaseAllResources",
    "EndScan",
    "ObsReset",
    "Restart",
    "Standby",
    "End",
    "Abort",
    "Restart",
    "GoToIdle",
    "ReleaseResources",
]


def test_set_delay(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    assert subarray_device.delay == 2
    subarray_device.SetDelay(5)
    assert subarray_device.delay == 5


def test_set_defective(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    assert not subarray_device.defective
    subarray_device.SetDefective(True)
    assert subarray_device.defective


def test_set_raise_exception(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    assert not subarray_device.raiseException
    subarray_device.SetRaiseException(True)
    assert subarray_device.raiseException


@pytest.mark.parametrize("command", commands_with_argin)
def test_command_with_argin(tango_context, command):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    result, message = subarray_device.command_inout(command, "")
    assert result[0] == ResultCode.OK
    assert message[0] == ""


@pytest.mark.parametrize("command", commands_without_argin)
def test_command_without_argin(tango_context, command):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    result, message = subarray_device.command_inout(command)
    assert result[0] == ResultCode.OK


def test_assign_resources_defective(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    subarray_device.SetDefective(True)
    result, message = subarray_device.AssignResources("")
    assert result[0] == ResultCode.FAILED
    assert (
        message[0] == "Device is Defective, cannot process command completely."
    )
    assert subarray_device.obsstate == ObsState.RESOURCING


def test_scan_command(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    result, message = subarray_device.Scan("")
    assert result[0] == ResultCode.OK
    assert subarray_device.obsstate == ObsState.SCANNING


@pytest.mark.u1
def test_release_resources_defective(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    subarray_device.SetDefective(True)
    result, message = subarray_device.ReleaseAllResources()
    assert result[0] == ResultCode.FAILED
    assert (
        message[0] == "Device is Defective, cannot process command completely."
    )
    assert subarray_device.obsstate == ObsState.RESOURCING
