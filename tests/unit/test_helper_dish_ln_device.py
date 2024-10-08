import json
import time
from datetime import datetime as dt

import numpy
import pytest
from ska_tango_base.commands import ResultCode
from tango import DevFailed

from ska_tmc_common import DevFactory, DishMode, FaultType, PointingState
from ska_tmc_common.test_helpers.constants import ABORT, CONFIGURE, RESTART
from tests.settings import (
    COMMAND_NOT_ALLOWED_DEFECT,
    DISH_LN_DEVICE,
    FAILED_RESULT_DEFECT,
    FAILED_RESULT_DEFECT_EXCEPTION,
    HELPER_SDP_QUEUE_CONNECTOR_DEVICE,
)

COMMANDS = [
    "SetStandbyFPMode",
    "SetStandbyLPMode",
    "SetOperateMode",
    "SetStowMode",
    "Off",
    "AbortCommands",
    "Configure",
    "Scan",
]
COMMANDS_WITHOUT_INPUT = [
    "SetStandbyFPMode",
    "SetStandbyLPMode",
    "SetOperateMode",
    "SetStowMode",
    "Off",
    "EndScan",
]


def test_attribute_on_helper_dish_ln_device(tango_context):
    dish_ln_device = DevFactory().get_device(DISH_LN_DEVICE)
    assert dish_ln_device.defective == json.dumps(
        {
            "enabled": False,
            "fault_type": FaultType.FAILED_RESULT,
            "error_message": "Default exception.",
            "result": ResultCode.FAILED,
        }
    )
    assert isinstance(dish_ln_device.actualPointing, str)
    assert dish_ln_device.kValueValidationResult == str(
        int(ResultCode.STARTED)
    )
    assert dish_ln_device.pointingState == PointingState.NONE
    assert dish_ln_device.dishMode == DishMode.STANDBY_LP
    assert dish_ln_device.commandDelayInfo == json.dumps(
        {
            CONFIGURE: 2,
            ABORT: 2,
            RESTART: 2,
        }
    )
    assert not dish_ln_device.commandCallInfo


@pytest.mark.parametrize("command", COMMANDS_WITHOUT_INPUT)
def test_dish_commands_without_input(tango_context, command):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_LN_DEVICE)
    result, command_id = dish_device.command_inout(command)
    command_call_info = dish_device.commandCallInfo
    assert command_call_info[0] == (command, "")
    assert result[0] == ResultCode.QUEUED
    assert isinstance(command_id[0], str)


def test_dish_commands_with_input(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_LN_DEVICE)
    result, _ = dish_device.command_inout("Configure", "")
    assert result[0] == ResultCode.QUEUED


def test_dish_ln_commands_scan(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_LN_DEVICE)
    result, command_id = dish_device.command_inout("Scan", "")
    assert result[0] == ResultCode.QUEUED
    assert isinstance(command_id[0], str)


def test_scan_command_without_argin_failed_result(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_LN_DEVICE)
    dish_device.SetDefective(json.dumps(FAILED_RESULT_DEFECT))
    result, message = dish_device.command_inout("Scan", "")
    assert result[0] == ResultCode.FAILED
    assert FAILED_RESULT_DEFECT_EXCEPTION in message[0]
    dish_device.SetDefective(json.dumps({"enabled": False}))


@pytest.mark.parametrize("command_to_check", COMMANDS_WITHOUT_INPUT)
def test_command_without_argin_failed_result(tango_context, command_to_check):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_LN_DEVICE)
    dish_device.SetDefective(json.dumps(FAILED_RESULT_DEFECT))
    result, message = dish_device.command_inout(command_to_check)
    assert result[0] == ResultCode.FAILED
    assert FAILED_RESULT_DEFECT_EXCEPTION in message[0]
    dish_device.SetDefective(json.dumps({"enabled": False}))


def test_command_with_argin_failed_result(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_LN_DEVICE)
    dish_device.SetDefective(json.dumps(FAILED_RESULT_DEFECT))
    result, message = dish_device.command_inout("Configure", "")
    assert result[0] == ResultCode.FAILED
    assert FAILED_RESULT_DEFECT_EXCEPTION in message[0]
    dish_device.SetDefective(json.dumps({"enabled": False}))


def test_Abort_commands(tango_context):
    dev_factory = DevFactory()
    dish_ln_device = dev_factory.get_device(DISH_LN_DEVICE)
    result, command_id = dish_ln_device.command_inout("AbortCommands")
    assert result[0] == ResultCode.OK
    assert isinstance(command_id[0], str)
    assert dish_ln_device.pointingState == PointingState.READY
    assert dish_ln_device.dishMode == DishMode.STANDBY_FP


@pytest.mark.parametrize("command_to_check", COMMANDS)
def test_dish_commands_command_not_allowed(tango_context, command_to_check):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_LN_DEVICE)
    # Set the device to the defective state with COMMAND_NOT_ALLOWED fault
    dish_device.SetDefective(json.dumps(COMMAND_NOT_ALLOWED_DEFECT))
    # Attempt to execute the command and expect the DevFailed exception
    with pytest.raises(DevFailed):
        dish_device.command_inout(command_to_check)
    # Clear the defect and ensure the command can be executed when not
    # defective
    dish_device.SetDefective(json.dumps({"enabled": False}))


@pytest.mark.skip(
    reason="This test case will not pass as "
    + "SetKValue command have tango database api"
)
def test_SetKValue_command_dishln(tango_context):
    """
    This test case invokes command on dish leaf node device
    and checks whether the attributes are populated with
    relevant k value or not.
    """
    dev_factory = DevFactory()
    dishln_device = dev_factory.get_device(DISH_LN_DEVICE)

    return_code, _ = dishln_device.SetKValue(5)
    return_code[0] = ResultCode.OK

    assert dishln_device.kValue == 5


def test_SetKValue_command_dishln_defective(tango_context):
    """
    This test case invokes command on dish leaf node device
    and checks whether the attributes are populated with
    relevant k value or not.
    """
    dev_factory = DevFactory()
    dishln_device = dev_factory.get_device(DISH_LN_DEVICE)
    dishln_device.SetDefective(json.dumps(FAILED_RESULT_DEFECT))
    return_code, error_message = dishln_device.SetKValue(5)

    assert return_code[0] == ResultCode.FAILED
    assert FAILED_RESULT_DEFECT_EXCEPTION in error_message[0]

    dishln_device.SetDefective(json.dumps({"enabled": False}))


def test_to_check_kvalidationresult_push_event(tango_context):
    """
    This test case checks kValuvalidationResult event gets pushed after
    invoking SetDirectkValueValidationResult command.
    """
    dev_factory = DevFactory()
    dishln_device = dev_factory.get_device(DISH_LN_DEVICE)
    # Wait for the device to initialize.
    start_time = time.time()
    elapsed_time = 0
    timeout = 20
    while elapsed_time <= timeout:
        if (
            str(int(ResultCode.UNKNOWN))
            == dishln_device.kValueValidationResult
        ):
            break
        time.sleep(1)
        elapsed_time = time.time() - start_time
    # Assert initial value is getting set
    assert dishln_device.kValueValidationResult == str(int(ResultCode.UNKNOWN))
    # Assert command is working as expected
    dishln_device.SetDirectkValueValidationResult(str(int(ResultCode.FAILED)))
    assert dishln_device.kValueValidationResult == str(int(ResultCode.FAILED))


def test_to_check_kvalidationresult_result_code_ok(tango_context):
    """
    This test case checks kValuvalidationResult event gets pushed after
    invoking SetDirectkValueValidationResult command.
    """
    dev_factory = DevFactory()
    dishln_device = dev_factory.get_device(DISH_LN_DEVICE)
    # Wait for the device to initialize.
    dishln_device.kValue = 5
    dishln_device.init()
    start_time = time.time()
    elapsed_time = 0
    timeout = 20
    while elapsed_time <= timeout:
        if str(int(ResultCode.OK)) == dishln_device.kValueValidationResult:
            break
        time.sleep(1)
        elapsed_time = time.time() - start_time
    # Assert initial value is getting set
    assert dishln_device.kValueValidationResult == str(int(ResultCode.OK))


def test_source_offset_dishln_attribute(tango_context):
    """
    This test case verifies sourceOffset dish leaf node attribute.
    """
    SOURCE_OFFSET = [0.0, 5.0]
    dev_factory = DevFactory()
    dishln_device = dev_factory.get_device(DISH_LN_DEVICE)
    dishln_device.SetSourceOffset(SOURCE_OFFSET)
    assert numpy.array_equal(SOURCE_OFFSET, dishln_device.sourceOffset)


def test_sdpQueueConnectorFqdn_dishln_attribute(tango_context):
    """
    This test case verifies sdpQueueConnectorFQDN dish leaf node attribute.
    """
    SDPQC_ATTR_PROXY = "test-sdp/queueconnector/01/pointing_cal_{dish_id}"
    timestamp = dt.now().strftime("%Y-%m-%d %H:%M:%S")
    dev_factory = DevFactory()
    dishln_device = dev_factory.get_device(DISH_LN_DEVICE)
    sdpqc_device = dev_factory.get_device(HELPER_SDP_QUEUE_CONNECTOR_DEVICE)
    dishln_device.sdpQueueConnectorFqdn = SDPQC_ATTR_PROXY
    sdpqc_device.SetPointingCalSka001([1.0, 2.0, 3.0])
    # Updated actualPointing with expected values
    updated_actual_pointing = [
        timestamp,
        285.2504396,
        74.8694392,
    ]

    timestamp, azimuth, elevation = updated_actual_pointing
    actual_pointing = json.loads(dishln_device.actualPointing)

    # Assert azimuth and elevation
    assert actual_pointing[1] == azimuth
    assert actual_pointing[2] == elevation

    # Compare timestamps up to minutes for a more lenient check
    timestamp_pointing = actual_pointing[0][:-3]  # up to minutes
    timestamp = timestamp[:-3]  # up to minutes
    assert (
        timestamp_pointing == timestamp
    ), f"Expected timestamp: '{timestamp}', but got: '{timestamp_pointing}'"
