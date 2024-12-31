import json

import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import AdminMode

from ska_tmc_common import DevFactory
from tests.settings import (
    CSP_LEAF_NODE_DEVICE,
    FAILED_RESULT_DEFECT,
    FAILED_RESULT_DEFECT_EXCEPTION,
)


def test_assign_resources_defective(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(CSP_LEAF_NODE_DEVICE)
    subarray_device.adminMode = AdminMode.ONLINE
    subarray_device.SetDefective(json.dumps(FAILED_RESULT_DEFECT))
    result, command_id = subarray_device.AssignResources("")
    assert result[0] == ResultCode.FAILED
    assert FAILED_RESULT_DEFECT_EXCEPTION in command_id[0]
    subarray_device.SetDefective(json.dumps({"enabled": False}))


def test_dish_ln_commands_scan(tango_context, group_callback):
    dev_factory = DevFactory()

    sdpln_device = dev_factory.get_device(CSP_LEAF_NODE_DEVICE)
    sdpln_device.adminMode = AdminMode.ONLINE
    sdpln_device.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        group_callback["longRunningCommandResult"],
    )
    result, command_id = sdpln_device.command_inout("Scan", "")
    assert result[0] == ResultCode.QUEUED
    assert isinstance(command_id[0], str)
    group_callback["longRunningCommandResult"].assert_change_event(
        (command_id[0], json.dumps((ResultCode.OK, "Command Completed"))),
        lookahead=3,
    )
