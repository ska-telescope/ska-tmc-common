import pytest
import tango
from tango import DevState

from tests.test_leaf_device import TestLeafDevice


@pytest.fixture(scope="module")
def devices_to_load():
    """
    This method contains the list of devices to load.
    :return: devices to load list
    """
    return (
        {
            "class": TestLeafDevice,
            "devices": [{"name": "test/leaf/d1"}],
        },
    )


def test_base_leaf_device(tango_context, group_callback):

    leaf_device = tango.DeviceProxy("test/leaf/d1")
    leaf_device.subscribe_event(
        "state", tango.EventType.CHANGE_EVENT, group_callback["state"]
    )
    leaf_device.push_state_event(DevState.ON)
