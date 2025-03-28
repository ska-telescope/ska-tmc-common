import json
from os.path import dirname, join

import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import AdminMode, ObsState
from tango import DevFailed, DevState

from ska_tmc_common import DevFactory, FaultType
from ska_tmc_common.test_helpers.helper_sdp_subarray import HelperSdpSubarray
from tests.settings import SDP_SUBARRAY_DEVICE, wait_for_obstate

commands_with_argin = ["AssignResources", "Scan", "Configure", "Scan"]


def get_assign_input_str(assign_input_file="tmc-sdp_AssignResources.json"):
    path = join(dirname(__file__), "data", assign_input_file)
    with open(path, "r") as f:
        assign_input_str = f.read()
    return assign_input_str


def get_configure_input_str(configure_input_file="tmc-sdp_Configure.json"):
    path = join(dirname(__file__), "data", configure_input_file)
    with open(path, "r") as f:
        configure_input_str = f.read()
    return configure_input_str


def get_scan_input_str(scan_input_file="tmc-sdp_Scan.json"):
    path = join(dirname(__file__), "data", scan_input_file)
    with open(path, "r") as f:
        scan_input_str = f.read()
    return scan_input_str


@pytest.fixture(scope="module")
def devices_to_load():
    return (
        {
            "class": HelperSdpSubarray,
            "devices": [{"name": SDP_SUBARRAY_DEVICE}],
        },
    )


def test_set_defective(tango_context):
    dev_factory = DevFactory()
    sdp_subarray_device = dev_factory.get_device(SDP_SUBARRAY_DEVICE)
    sdp_subarray_device.adminMode = AdminMode.ONLINE
    defect = {
        "enabled": True,
        "fault_type": FaultType.FAILED_RESULT,
        "error_message": (
            "Device is defective, cannot process command." "completely."
        ),
        "result": ResultCode.FAILED,
    }
    sdp_subarray_device.SetDefective(json.dumps(defect))
    assert sdp_subarray_device.defective
    sdp_subarray_device.SetDefective(json.dumps({"enabled": False}))


def test_on_command(tango_context):
    dev_factory = DevFactory()
    sdp_subarray_device = dev_factory.get_device(SDP_SUBARRAY_DEVICE)
    sdp_subarray_device.adminMode = AdminMode.ONLINE
    sdp_subarray_device.On()
    assert sdp_subarray_device.state() == DevState.ON


def test_off_command(tango_context):
    dev_factory = DevFactory()
    sdp_subarray_device = dev_factory.get_device(SDP_SUBARRAY_DEVICE)
    sdp_subarray_device.adminMode = AdminMode.ONLINE
    sdp_subarray_device.Off()
    assert sdp_subarray_device.state() == DevState.OFF


def test_release_command(tango_context):
    dev_factory = DevFactory()
    sdp_subarray_device = dev_factory.get_device(SDP_SUBARRAY_DEVICE)
    sdp_subarray_device.adminMode = AdminMode.ONLINE
    sdp_subarray_device.ReleaseResources()
    wait_for_obstate(sdp_subarray_device, ObsState.IDLE)


def test_release_all_command(tango_context):
    dev_factory = DevFactory()
    sdp_subarray_device = dev_factory.get_device(SDP_SUBARRAY_DEVICE)
    sdp_subarray_device.adminMode = AdminMode.ONLINE
    sdp_subarray_device.ReleaseAllResources()
    wait_for_obstate(sdp_subarray_device, ObsState.EMPTY)


def test_endscan_command(tango_context):
    dev_factory = DevFactory()
    sdp_subarray_device = dev_factory.get_device(SDP_SUBARRAY_DEVICE)
    sdp_subarray_device.adminMode = AdminMode.ONLINE
    sdp_subarray_device.EndScan()
    wait_for_obstate(sdp_subarray_device, ObsState.READY)


def test_end_command(tango_context):
    dev_factory = DevFactory()
    sdp_subarray_device = dev_factory.get_device(SDP_SUBARRAY_DEVICE)
    sdp_subarray_device.adminMode = AdminMode.ONLINE
    sdp_subarray_device.End()
    wait_for_obstate(sdp_subarray_device, ObsState.IDLE)


def test_abort_command(tango_context):
    dev_factory = DevFactory()
    sdp_subarray_device = dev_factory.get_device(SDP_SUBARRAY_DEVICE)
    sdp_subarray_device.adminMode = AdminMode.ONLINE
    sdp_subarray_device.Abort()
    wait_for_obstate(sdp_subarray_device, ObsState.ABORTING)
    wait_for_obstate(sdp_subarray_device, ObsState.ABORTED)


def test_restart_command(tango_context):
    dev_factory = DevFactory()
    sdp_subarray_device = dev_factory.get_device(SDP_SUBARRAY_DEVICE)
    sdp_subarray_device.adminMode = AdminMode.ONLINE
    sdp_subarray_device.Restart()
    wait_for_obstate(sdp_subarray_device, ObsState.EMPTY)


def test_assign_resources_valid_input(tango_context):
    dev_factory = DevFactory()
    sdp_subarray_device = dev_factory.get_device(SDP_SUBARRAY_DEVICE)
    sdp_subarray_device.adminMode = AdminMode.ONLINE
    assign_input_str = get_assign_input_str()
    sdp_subarray_device.AssignResources(assign_input_str)
    wait_for_obstate(sdp_subarray_device, ObsState.IDLE)


def test_assign_resources_invalid_input_missing_eb_id(tango_context):
    dev_factory = DevFactory()
    sdp_subarray_device = dev_factory.get_device(SDP_SUBARRAY_DEVICE)
    sdp_subarray_device.adminMode = AdminMode.ONLINE
    assign_input_str = get_assign_input_str()
    input_string = json.loads(assign_input_str)
    del input_string["execution_block"]["eb_id"]
    with pytest.raises(
        DevFailed, match="Missing eb_id in the AssignResources input json"
    ):
        sdp_subarray_device.AssignResources(json.dumps(input_string))
    assert sdp_subarray_device.obsState == ObsState.EMPTY


def test_assign_resources_invalid_input_missing_resources(tango_context):
    dev_factory = DevFactory()
    sdp_subarray_device = dev_factory.get_device(SDP_SUBARRAY_DEVICE)
    sdp_subarray_device.adminMode = AdminMode.ONLINE
    assign_input_str = get_assign_input_str()
    input_string = json.loads(assign_input_str)
    defect = {
        "enabled": True,
        "fault_type": FaultType.SDP_FAULT,
        "error_message": (
            "Missing receive nodes in the AssignResources input json"
        ),
    }
    sdp_subarray_device.SetDefective(json.dumps(defect))
    with pytest.raises(
        DevFailed,
        match="Missing receive nodes in the AssignResources input json",
    ):
        sdp_subarray_device.AssignResources(json.dumps(input_string))
    assert sdp_subarray_device.obsState == ObsState.FAULT


def test_assign_resources_missing_resources_key(tango_context):
    """
    Test when 'resources' key is missing from input_json.
    """
    dev_factory = DevFactory()
    sdp_subarray_device = dev_factory.get_device(SDP_SUBARRAY_DEVICE)
    sdp_subarray_device.adminMode = AdminMode.ONLINE
    assign_input_str = get_assign_input_str()
    input_string = json.loads(assign_input_str)
    input_string.pop("resources")  # Remove the 'resources' key

    sdp_subarray_device.AssignResources(json.dumps(input_string))

    wait_for_obstate(sdp_subarray_device, ObsState.IDLE)


def test_configure_valid_input(tango_context):
    dev_factory = DevFactory()
    sdp_subarray_device = dev_factory.get_device(SDP_SUBARRAY_DEVICE)
    sdp_subarray_device.adminMode = AdminMode.ONLINE
    configure_input_str = get_configure_input_str()
    sdp_subarray_device.Configure(configure_input_str)
    wait_for_obstate(sdp_subarray_device, ObsState.READY)


def test_configure_invalid_input(tango_context):
    dev_factory = DevFactory()
    sdp_subarray_device = dev_factory.get_device(SDP_SUBARRAY_DEVICE)
    sdp_subarray_device.adminMode = AdminMode.ONLINE
    assign_input_str = get_assign_input_str()
    sdp_subarray_device.AssignResources(assign_input_str)
    wait_for_obstate(sdp_subarray_device, ObsState.IDLE)
    configure_input_str = get_configure_input_str()
    input_string = json.loads(configure_input_str)
    del input_string["scan_type"]
    with pytest.raises(
        DevFailed, match="Missing scan_type in the Configure input json"
    ):
        sdp_subarray_device.Configure(json.dumps(input_string))
    assert sdp_subarray_device.obsState == ObsState.IDLE


def test_scan_valid_input(tango_context):
    dev_factory = DevFactory()
    sdp_subarray_device = dev_factory.get_device(SDP_SUBARRAY_DEVICE)
    sdp_subarray_device.adminMode = AdminMode.ONLINE
    scan_input_str = get_scan_input_str()
    sdp_subarray_device.Scan(scan_input_str)
    wait_for_obstate(sdp_subarray_device, ObsState.SCANNING)


def test_scan_invalid_input(tango_context):
    dev_factory = DevFactory()
    sdp_subarray_device = dev_factory.get_device(SDP_SUBARRAY_DEVICE)
    sdp_subarray_device.adminMode = AdminMode.ONLINE
    assign_input_str = get_assign_input_str()
    sdp_subarray_device.AssignResources(assign_input_str)
    wait_for_obstate(sdp_subarray_device, ObsState.IDLE)
    configure_input_str = get_configure_input_str()
    sdp_subarray_device.Configure(configure_input_str)
    wait_for_obstate(sdp_subarray_device, ObsState.READY)
    scan_input_str = get_scan_input_str()
    input_string = json.loads(scan_input_str)
    del input_string["scan_id"]
    with pytest.raises(
        DevFailed, match="Missing scan_id in the Scan input json"
    ):
        sdp_subarray_device.Scan(json.dumps(input_string))
    assert sdp_subarray_device.obsState == ObsState.READY


def test_release_resources_defective(tango_context):
    dev_factory = DevFactory()
    sdp_subarray_device = dev_factory.get_device(SDP_SUBARRAY_DEVICE)
    sdp_subarray_device.adminMode = AdminMode.ONLINE
    # Check ReleaseAllResources Defective
    defect = {
        "enabled": True,
        "fault_type": FaultType.FAILED_RESULT,
        "error_message": "Device failed with exception",
        "result": ResultCode.FAILED,
    }

    sdp_subarray_device.SetDefective(json.dumps(defect))
    with pytest.raises(DevFailed, match="Exception occurred, command failed"):
        sdp_subarray_device.ReleaseAllResources()
    sdp_subarray_device.SetDefective(json.dumps({"enabled": False}))


def test_sdp_receive_addresses(tango_context, json_factory):
    dev_factory = DevFactory()
    sdp_subarray_device = dev_factory.get_device(SDP_SUBARRAY_DEVICE)
    sdp_subarray_device.adminMode = AdminMode.ONLINE
    receive_addr = json_factory("ReceiveAddresses_mid")
    sdp_subarray_device.SetDirectreceiveAddresses(receive_addr)
    assert sdp_subarray_device.receiveAddresses == receive_addr


def test_sdp_low_receive_address(sdp_subarray_low):
    """Test to verify number of items in the port key"""
    low_sdp_subarray = sdp_subarray_low
    receive_addresses_value = json.loads(low_sdp_subarray.receiveAddresses)
    assert len(receive_addresses_value["science_A"]["vis0"]["port"][0]) == 3
    assert len(receive_addresses_value["science_A"]["vis0"]["port"][1]) == 3
    assert len(receive_addresses_value["target:a"]["vis0"]["port"][0]) == 3
    assert len(receive_addresses_value["target:a"]["vis0"]["port"][1]) == 3
    assert (
        len(receive_addresses_value["calibration:b"]["vis0"]["port"][0]) == 3
    )
    assert (
        len(receive_addresses_value["calibration:b"]["vis0"]["port"][1]) == 3
    )


def test_sdp_mid_receive_address(sdp_subarray_mid):
    """Test to verify number of items in the port key"""
    low_sdp_subarray = sdp_subarray_mid
    receive_addresses_value = json.loads(low_sdp_subarray.receiveAddresses)
    assert len(receive_addresses_value["science_A"]["vis0"]["port"][0]) == 2
    assert len(receive_addresses_value["science_A"]["vis0"]["port"][1]) == 2
    assert len(receive_addresses_value["target:a"]["vis0"]["port"][0]) == 2
    assert len(receive_addresses_value["target:a"]["vis0"]["port"][1]) == 2
    assert (
        len(receive_addresses_value["calibration:b"]["vis0"]["port"][0]) == 2
    )
    assert (
        len(receive_addresses_value["calibration:b"]["vis0"]["port"][1]) == 2
    )
