import json

import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState

from ska_tmc_common import DevFactory, FaultType
from tests.settings import (
    DEFAULT_DEFECT_SETTINGS,
    HELPER_MCCS_CONTROLLER,
    MCCS_SUBARRAY_DEVICE,
    wait_for_obstate,
)

allocate_argin_string = json.dumps(
    {
        "interface": "https://schema.skao.int/ska-low-mccs-controller-allocate/3.0",  # noqa
        "subarray_id": 1,
        "subarray_beams": [
            {
                "subarray_beam_id": 3,
                "apertures": [
                    {"station_id": 1, "aperture_id": "1.1"},
                    {"station_id": 2, "aperture_id": "2.2"},
                    {"station_id": 2, "aperture_id": "2.3"},
                    {"station_id": 3, "aperture_id": "3.1"},
                    {"station_id": 4, "aperture_id": "4.1"},
                ],
            }
        ],
    }
)
release_argin_string = json.dumps({"subarray_id": 1, "release_all": True})

commands_without_argin = ["On", "Off"]


def test_mccs_controller_release_command(tango_context):
    dev_factory = DevFactory()
    mccs_controller_device = dev_factory.get_device(HELPER_MCCS_CONTROLLER)
    result, unique_id = mccs_controller_device.command_inout(
        "Release", release_argin_string
    )
    mccs_subarray_device = dev_factory.get_device(MCCS_SUBARRAY_DEVICE)
    assert result[0] == ResultCode.QUEUED
    assert unique_id[0].endswith("Release")
    wait_for_obstate(mccs_subarray_device, ObsState.EMPTY)
    assert mccs_subarray_device.obsstate == ObsState.EMPTY


def test_mccs_controller_allocate_command(tango_context):
    dev_factory = DevFactory()
    mccs_controller_device = dev_factory.get_device(HELPER_MCCS_CONTROLLER)
    result, unique_id = mccs_controller_device.command_inout(
        "Allocate", allocate_argin_string
    )
    mccs_subarray_device = dev_factory.get_device(MCCS_SUBARRAY_DEVICE)
    assert result[0] == ResultCode.QUEUED
    assert unique_id[0].endswith("Allocate")
    assert mccs_subarray_device.obsstate == ObsState.RESOURCING
    wait_for_obstate(mccs_subarray_device, ObsState.IDLE)
    assert mccs_subarray_device.obsstate == ObsState.IDLE


@pytest.mark.parametrize("command", commands_without_argin)
def test_mccs_controller_commands_without_argument(tango_context, command):
    dev_factory = DevFactory()
    mccs_controller_device = dev_factory.get_device(HELPER_MCCS_CONTROLLER)
    result, command_id = mccs_controller_device.command_inout(command)
    assert result[0] == ResultCode.QUEUED
    assert isinstance(command_id[0], str)


def test_mccs_controller_allocate_defective(tango_context):
    dev_factory = DevFactory()
    mccs_controller_device = dev_factory.get_device(HELPER_MCCS_CONTROLLER)
    mccs_controller_device.SetDefective(json.dumps(DEFAULT_DEFECT_SETTINGS))
    result, command_id = mccs_controller_device.command_inout(
        "Allocate", allocate_argin_string
    )
    assert result[0] == ResultCode.FAILED
    assert "Allocate" in command_id[0]


def test_mccs_controller_release_defective(tango_context):
    dev_factory = DevFactory()
    mccs_controller_device = dev_factory.get_device(HELPER_MCCS_CONTROLLER)
    mccs_controller_device.SetDefective(json.dumps(DEFAULT_DEFECT_SETTINGS))
    result, command_id = mccs_controller_device.command_inout(
        "Release", release_argin_string
    )
    assert result[0] == ResultCode.FAILED
    assert "Release" in command_id[0]


def test_allocate_stuck_in_intermediate_state(tango_context):
    dev_factory = DevFactory()
    mccs_controller_device = dev_factory.get_device(HELPER_MCCS_CONTROLLER)
    mccs_subarray_device = dev_factory.get_device(MCCS_SUBARRAY_DEVICE)
    defect = {
        "enabled": True,
        "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
        "result": ResultCode.FAILED,
        "error_message": "Device is stuck in Resourcing state",
        "intermediate_state": ObsState.RESOURCING,
    }
    mccs_subarray_device.SetDefective(json.dumps(defect))
    result, _ = mccs_controller_device.command_inout(
        "Allocate", allocate_argin_string
    )
    assert result[0] == ResultCode.QUEUED
    with pytest.raises(Exception) as exception:
        wait_for_obstate(mccs_subarray_device, ObsState.IDLE)

    message_to_assert = (
        f"Timeout occured while waiting for {MCCS_SUBARRAY_DEVICE} ObsState to"
        + f" transition to {ObsState.IDLE}. Current obsState is "
        + f"{ObsState.RESOURCING}"
    )
    assert message_to_assert == str(exception.value)
    mccs_controller_device.SetDefective(json.dumps({"enabled": False}))


def test_restart_subarray_command(tango_context):
    dev_factory = DevFactory()
    mccs_controller_device = dev_factory.get_device(HELPER_MCCS_CONTROLLER)
    mccs_subarray_device = dev_factory.get_device(MCCS_SUBARRAY_DEVICE)
    # Provide the subarray ID as an argument to the RestartSubarray command
    subarray_id = 1
    result = mccs_controller_device.command_inout(
        "RestartSubarray", subarray_id
    )
    assert result[0] == ResultCode.QUEUED
    wait_for_obstate(mccs_subarray_device, ObsState.EMPTY)
    assert mccs_subarray_device.obsstate == ObsState.EMPTY
