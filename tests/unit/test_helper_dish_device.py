import json
import logging
from datetime import datetime

import numpy as np
import pytest
from astropy.time import Time
from ska_tango_base.commands import ResultCode
from tango import DevFailed

from ska_tmc_common import DevFactory
from ska_tmc_common.enum import DishMode, PointingState
from tests.settings import (
    COMMAND_NOT_ALLOWED_DEFECT,
    DISH_DEVICE,
    FAILED_RESULT_DEFECT,
    FAILED_RESULT_DEFECT_EXCEPTION,
)

logger = logging.getLogger(__name__)

COMMANDS = [
    "SetStandbyFPMode",
    "SetStandbyLPMode",
    "SetOperateMode",
    "SetStowMode",
    "Scan",
    "AbortCommands",
    "ConfigureBand1",
    "ConfigureBand2",
    "ConfigureBand3",
    "ConfigureBand4",
    "ConfigureBand5a",
    "ConfigureBand5b",
]
COMMANDS_WITHOUT_INPUT = [
    "SetStandbyFPMode",
    "SetStandbyLPMode",
    "SetOperateMode",
    "SetStowMode",
    "EndScan",
]
COMMANDS_WITH_INPUT = [
    "ConfigureBand1",
    "ConfigureBand2",
    "ConfigureBand3",
    "ConfigureBand4",
    "ConfigureBand5a",
    "ConfigureBand5b",
]


def test_set_delay(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    dish_device.SetDelayInfo('{"Configure": 3}')
    command_delay_info = json.loads(dish_device.commandDelayInfo)
    assert command_delay_info["Configure"] == 3


def test_program_track_table(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    programTrackTable_example = np.array(
        [
            1706629796036.8691,
            181.223951890779,
            31.189377349638,
            1706629796036.9192,
            181.223951890779,
            31.189377349638,
            1706629796036.969,
            181.223951890779,
            31.189377349638,
            1706629796037.019,
            181.223951890779,
            31.189377349638,
            1706629796037.069,
            181.223951890779,
            31.189377349638,
        ]
    )

    dish_device.programTrackTable = programTrackTable_example
    assert np.array_equal(
        dish_device.programTrackTable, np.array(programTrackTable_example)
    )


@pytest.mark.parametrize("command", COMMANDS_WITHOUT_INPUT)
def test_dish_commands_without_input(tango_context, command):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    result, command_id = dish_device.command_inout(command)
    command_call_info = dish_device.commandCallInfo
    assert command_call_info[0][0] == command
    assert result[0] == ResultCode.QUEUED
    assert command in command_id[0]


@pytest.mark.parametrize("command", COMMANDS_WITH_INPUT)
def test_dish_commands_with_input(tango_context, command):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    result, command_id = dish_device.command_inout(command, True)
    assert result[0] == ResultCode.QUEUED
    assert command in command_id[0]


def test_dish_commands_scan(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    result, command_id = dish_device.command_inout("Scan", "")
    assert result[0] == ResultCode.QUEUED
    assert "Scan" in command_id[0]


def test_scan_command_without_argin_failed_result(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    dish_device.SetDefective(json.dumps(FAILED_RESULT_DEFECT))
    result, message = dish_device.command_inout("Scan", "")
    assert result[0] == ResultCode.FAILED
    assert FAILED_RESULT_DEFECT_EXCEPTION in message[0]
    dish_device.SetDefective(json.dumps({"enabled": False}))


@pytest.mark.parametrize("command_to_check", COMMANDS_WITHOUT_INPUT)
def test_command_without_argin_failed_result(tango_context, command_to_check):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    dish_device.SetDefective(json.dumps(FAILED_RESULT_DEFECT))
    result, message = dish_device.command_inout(command_to_check)
    assert result[0] == ResultCode.FAILED
    assert FAILED_RESULT_DEFECT_EXCEPTION in message[0]
    dish_device.SetDefective(json.dumps({"enabled": False}))


@pytest.mark.parametrize("command_to_check", COMMANDS_WITH_INPUT)
def test_command_with_argin_failed_result(tango_context, command_to_check):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    dish_device.SetDefective(json.dumps(FAILED_RESULT_DEFECT))
    result, message = dish_device.command_inout(command_to_check, True)
    assert result[0] == ResultCode.FAILED
    assert FAILED_RESULT_DEFECT_EXCEPTION in message[0]
    dish_device.SetDefective(json.dumps({"enabled": False}))


def test_Abort_commands(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    result, command_id = dish_device.command_inout("AbortCommands")
    assert result[0] == ResultCode.OK
    assert "AbortCommands" in command_id[0]
    assert dish_device.pointingState == PointingState.READY
    assert dish_device.dishMode == DishMode.STANDBY_FP


@pytest.mark.parametrize("command_to_check", COMMANDS)
def test_dish_commands_command_not_allowed(tango_context, command_to_check):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    # Set the device to the defective state with COMMAND_NOT_ALLOWED fault
    dish_device.SetDefective(json.dumps(COMMAND_NOT_ALLOWED_DEFECT))
    # Attempt to execute the command and expect the DevFailed exception
    with pytest.raises(DevFailed):
        dish_device.command_inout(command_to_check)
    # Clear the defect and ensure the command
    # can be executed when not defective
    dish_device.SetDefective(json.dumps({"enabled": False}))


def test_dish_SetKValue_command(tango_context):
    """
    This test case invokes command on dish master device
    and checks whether the attributes are populated with
    relevant k value or not.
    """
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)

    return_code, _ = dish_device.SetKValue(1)
    return_code[0] = ResultCode.OK

    assert dish_device.kValue == 1


def test_achived_pointing(tango_context):
    """Test to check timestamp is SKA epoch TAI format."""
    ska_epoch_tai = Time("1999-12-31T23:59:28Z", scale="utc").unix_tai
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    dish_tai_timestamp = float(dish_device.achievedPointing[0])
    current_date = datetime.now().strftime("%Y-%m-%d")
    tai_date = datetime.fromtimestamp(
        Time(
            dish_tai_timestamp + ska_epoch_tai, format="unix_tai", scale="tai"
        ).unix
    ).strftime("%Y-%m-%d")
    assert current_date == tai_date


def test_static_pm_setup_command(tango_context, json_factory):
    """This test verifies the functioning of ApplyPointingModel command"""
    dev_factory = DevFactory()
    dish_master_device = dev_factory.get_device(DISH_DEVICE)
    global_pointing_data = json_factory("global_pointing_model")
    result, command_id = dish_master_device.ApplyPointingModel(
        global_pointing_data
    )
    assert result[0] == ResultCode.QUEUED
    assert "ApplyPointingModel" in command_id[0]


def test_static_pm_setup_command_with_faulty_json(tango_context, json_factory):
    """This test verifies the JSONDecodeError of ApplyPointingModel command"""
    dev_factory = DevFactory()
    dish_master_device = dev_factory.get_device(DISH_DEVICE)

    # Read the file and store the lines
    with open("tests/data/global_pointing_model.json", "r") as file:
        lines = file.readlines()
    second_line = lines[1].strip()

    # Make the json faulty
    lines[1] = "abc," + "\n"
    with open("tests/data/global_pointing_model.json", "w") as file:
        file.writelines(lines)
    global_pointing_data = json_factory("global_pointing_model")

    # Test the command is reporting faulty JSON
    result, command_id = dish_master_device.ApplyPointingModel(
        global_pointing_data
    )
    assert result[0] == ResultCode.FAILED
    assert "Failed to decode JSON" in command_id[0]

    # Restore the JSON
    lines[1] = second_line + "\n"
    with open("tests/data/global_pointing_model.json", "w") as file:
        file.writelines(lines)
