import json
import logging

import numpy as np
import pytest
from ska_tango_base.commands import ResultCode
from tango import DevFailed

from ska_tmc_common import DevFactory
from tests.settings import (
    COMMAND_NOT_ALLOWED_DEFECT,
    DISH_DEVICE,
    FAILED_RESULT_DEFECT,
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
    "AbortCommands",
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
    dish_device.SetDelay('{"Configure": 3}')
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
    result, message = dish_device.command_inout(command)
    command_call_info = dish_device.commandCallInfo
    assert command_call_info[0][0] == command
    assert result[0] == ResultCode.OK
    assert message[0] == ""


@pytest.mark.parametrize("command", COMMANDS_WITH_INPUT)
def test_dish_commands_with_input(tango_context, command):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    result, message = dish_device.command_inout(command, True)
    assert result[0] == ResultCode.OK
    assert message[0] == ""


def test_dish_commands_scan(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    result, message = dish_device.command_inout("Scan", "")
    assert result[0] == ResultCode.OK
    assert message[0] == ""


@pytest.mark.parametrize("command_to_check", COMMANDS_WITHOUT_INPUT)
def test_command_without_argin_failed_result(tango_context, command_to_check):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    dish_device.SetDefective(json.dumps(FAILED_RESULT_DEFECT))
    result, message = dish_device.command_inout(command_to_check)
    assert result[0] == ResultCode.FAILED
    assert (
        message[0] == "Device is defective, cannot process command completely."
    )
    dish_device.SetDefective(json.dumps({"enabled": False}))


@pytest.mark.parametrize("command_to_check", COMMANDS_WITH_INPUT)
def test_command_with_argin_failed_result(tango_context, command_to_check):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    dish_device.SetDefective(json.dumps(FAILED_RESULT_DEFECT))
    result, message = dish_device.command_inout(command_to_check, True)
    assert result[0] == ResultCode.FAILED
    assert (
        message[0] == "Device is defective, cannot process command completely."
    )
    dish_device.SetDefective(json.dumps({"enabled": False}))


def test_Abort_commands(tango_context):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    result, message = dish_device.command_inout("AbortCommands")
    assert result[0] == ResultCode.OK
    assert message[0] == ""


@pytest.mark.parametrize("command_to_check", COMMANDS)
def test_dish_commands_command_not_allowed(tango_context, command_to_check):
    dev_factory = DevFactory()
    dish_device = dev_factory.get_device(DISH_DEVICE)
    # Set the device to the defective state with COMMAND_NOT_ALLOWED fault
    dish_device.SetDefective(json.dumps(COMMAND_NOT_ALLOWED_DEFECT))
    # Attempt to execute the command and expect the DevFailed exception
    with pytest.raises(DevFailed):
        dish_device.command_inout(command_to_check)
    # Clear the defect and ensure the command can be executed when not defective
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
