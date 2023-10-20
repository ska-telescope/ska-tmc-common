import json
import logging

import pytest
from ska_tango_base.commands import ResultCode

from ska_tmc_common import DevFactory
from tests.settings import HELPER_MCCS_CONTROLLER

commands_with_argin = ["Allocate", "Release"]
commands_without_argin = ["On", "Off"]

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("command", commands_with_argin)
def test_mccs_controller_commands_with_argument(tango_context, command):
    dev_factory = DevFactory()
    mccs_controller_device = dev_factory.get_device(HELPER_MCCS_CONTROLLER)
    result, message = mccs_controller_device.command_inout(command, "")
    logger.info(f"Result:{result},message:{message}")
    assert result[0] == ResultCode.QUEUED
    assert message[0] == ""


@pytest.mark.parametrize("command", commands_without_argin)
def test_mccs_controller_commands_without_argument(tango_context, command):
    dev_factory = DevFactory()
    mccs_controller_device = dev_factory.get_device(HELPER_MCCS_CONTROLLER)
    result, message = mccs_controller_device.command_inout(command)
    assert result[0] == ResultCode.QUEUED
    assert message[0] == ""


@pytest.mark.parametrize("command", commands_with_argin)
def test_mccs_controller_command_defective(tango_context, command):
    dev_factory = DevFactory()
    mccs_controller_device = dev_factory.get_device(HELPER_MCCS_CONTROLLER)
    mccs_controller_device.SetDefective(json.dumps({"enabled": True}))
    result, message = mccs_controller_device.command_inout(command, "")
    assert result[0] == ResultCode.FAILED
    assert message[0] == "Default exception."


@pytest.mark.parametrize("command", commands_with_argin)
def test_mccs_controller_command_raise_exception(tango_context, command):
    dev_factory = DevFactory()
    mccs_controller_device = dev_factory.get_device(HELPER_MCCS_CONTROLLER)
    mccs_controller_device.SetRaiseException(True)
    result, message = mccs_controller_device.command_inout(command, "")
    assert result[0] == ResultCode.QUEUED


# def test_allocate_stuck_in_intermediate_state(tango_context):
#     dev_factory = DevFactory()
#     subarray_leaf_device = dev_factory.get_device(SDP_LEAF_NODE_DEVICE)
#     defect = {
#         "enabled": True,
#         "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
#         "result": ResultCode.FAILED,
#         "intermediate_state": ObsState.RESOURCING,
#     }
#     subarray_leaf_device.SetDefective(json.dumps(defect))
#     result, _ = subarray_leaf_device.AssignResources("")
#     assert result[0] == ResultCode.QUEUED
#     assert subarray_leaf_device.obsState == ObsState.RESOURCING
#     subarray_leaf_device.SetDefective(json.dumps({"enabled": False}))
