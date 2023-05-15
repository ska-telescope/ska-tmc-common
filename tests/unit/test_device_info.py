import pytest
from ska_tmc_common import DeviceInfo
from tango import DevState
from ska_tango_base.control_model import HealthState

@pytest.mark.testping
def test_ping():
    dev_name = "ska_mid/tm_leaf_node/csp_subarray01" #testing device
    dev_info = DeviceInfo(dev_name ,True)
    assert dev_info.ping == -1
    dev_info.update_unresponsive(False)
    dev_info.ping = 100
    assert dev_info.ping == 100

@pytest.mark.testresp
def test_unresponsive():
    dev_name = "ska_mid/tm_leaf_node/csp_subarray01" #testing device
    dev_info = DeviceInfo(dev_name)
    assert dev_info.unresponsive==False
    dev_info.update_unresponsive(True)
    assert dev_info.unresponsive

@pytest.mark.testresp
def test_update_responsiveness():
    dev_name = "ska_mid/tm_leaf_node/csp_subarray01" #testing device
    dev_info = DeviceInfo(dev_name)
    assert dev_info.unresponsive == False
    dev_info.update_unresponsive(True, "Test exception")
    assert dev_info.unresponsive
    assert dev_info.state== DevState.UNKNOWN
    assert dev_info.health_state== HealthState.UNKNOWN
    assert dev_info.ping== -1
    assert dev_info.exception== "Test exception"

def test_to_dict():
        dev_name = "ska_mid/tm_leaf_node/csp_subarray01"
        dev_info = DeviceInfo(dev_name)
        dev_dict = dev_info.to_dict()
        isinstance(dev_dict, dict)
        dev_dict["dev_name"]== dev_name
        assert dev_dict["state"] == "DevState.UNKNOWN"
        assert dev_dict["healthState"]=="HealthState.UNKNOWN"
        assert dev_dict["ping"]== "-1"
        dev_dict["unresponsive"]==False