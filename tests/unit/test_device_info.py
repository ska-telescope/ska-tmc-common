from ska_tango_base.control_model import HealthState
from tango import DevState

from ska_tmc_common import DeviceInfo, SdpQueueConnectorDeviceInfo


def test_ping(csp_sln_dev_name):
    dev_info = DeviceInfo(csp_sln_dev_name, True)
    assert dev_info.ping == -1
    dev_info.update_unresponsive(False)
    dev_info.ping = 100
    assert dev_info.ping == 100


def test_unresponsive(csp_sln_dev_name):
    dev_info = DeviceInfo(csp_sln_dev_name)
    assert dev_info.unresponsive is False
    dev_info.update_unresponsive(True)
    assert dev_info.unresponsive


def test_update_responsiveness(csp_sln_dev_name):
    dev_info = DeviceInfo(csp_sln_dev_name)
    assert dev_info.unresponsive is False
    dev_info.update_unresponsive(True, "Test exception")
    assert dev_info.unresponsive
    assert dev_info.state == DevState.UNKNOWN
    assert dev_info.health_state == HealthState.UNKNOWN
    assert dev_info.ping == -1
    assert dev_info.exception == "Test exception"


def test_to_dict(csp_sln_dev_name):
    dev_info = DeviceInfo(csp_sln_dev_name)
    dev_dict = dev_info.to_dict()
    isinstance(dev_dict, dict)
    dev_dict["dev_name"] == csp_sln_dev_name
    assert dev_dict["state"] == "DevState.UNKNOWN"
    assert dev_dict["healthState"] == "HealthState.UNKNOWN"
    assert dev_dict["ping"] == "-1"
    dev_dict["unresponsive"] is False


def test_sdpqc_device_info():
    sdp_queue_connector_device_info = SdpQueueConnectorDeviceInfo()
    dev_name = "mid-sdp/queueconnector/01"
    pointing_data = [1.1, 2.2, 3.3]
    event_id = 1
    flag = True
    sdp_queue_connector_device_info.dev_name = dev_name
    sdp_queue_connector_device_info.pointing_data = pointing_data
    sdp_queue_connector_device_info.event_id = event_id
    sdp_queue_connector_device_info.subscribed_to_attribute = flag

    assert sdp_queue_connector_device_info.dev_name == dev_name
    assert sdp_queue_connector_device_info.event_id == event_id
    assert sdp_queue_connector_device_info.pointing_data == pointing_data
    assert sdp_queue_connector_device_info.subscribed_to_attribute == flag
