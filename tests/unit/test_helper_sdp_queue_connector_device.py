import numpy as np

from ska_tmc_common import DevFactory
from tests.settings import HELPER_SDP_QUEUE_CONNECTOR_DEVICE

# POINTING_CAL = [scanID, cross_elevation_offset, elevation_offset ]
POINTING_CAL_SKA001 = [1.0, 2.0, 3.0]
POINTING_CAL_SKA002 = [4.0, 5.0, 6.0]
POINTING_CAL_SKA003 = [7.0, 8.0, 9.0]
POINTING_CAL_SKA004 = [10.0, 11.0, 12.0]
POINTING_CAL_SKA036 = [13.0, 14.0, 15.0]
POINTING_CAL_SKA063 = [16.0, 17.0, 18.0]
POINTING_CAL_SKA100 = [19.0, 20.0, 21.0]


def test_pointing_offsets(tango_context):
    """This test verifies sdp queue connector pointing cal attribute"""

    DISH_DEVICE_LIST = [
        "SKA001",
        "SKA002",
        "SKA003",
        "SKA004",
        "SKA063",
        "SKA036",
        "SKA100",
    ]

    dev_factory = DevFactory()
    sdp_queue_connector_device = dev_factory.get_device(
        HELPER_SDP_QUEUE_CONNECTOR_DEVICE
    )

    # Raise event on pointing_cal_SKA001 attribute
    for dish_id in DISH_DEVICE_LIST:
        constant_name = f"POINTING_CAL_{dish_id}"
        constant = globals().get(constant_name)
        # Call the SetPointingCal method with the obtained constant
        dish_id = dish_id.capitalize()
        method_name = f"SetPointingCal{dish_id}"
        method = getattr(sdp_queue_connector_device, method_name)
        method(constant)

    for dish_id in DISH_DEVICE_LIST:
        attribute_name = f"pointing_cal_{dish_id}"
        constant_name = f"POINTING_CAL_{dish_id}"
        attribute_value = getattr(sdp_queue_connector_device, attribute_name)
        constant = globals().get(constant_name)
        # Assert that the attribute value equals the constant value
        assert np.array_equal(attribute_value, constant)
