import numpy

from ska_tmc_common import DevFactory
from tests.settings import HELPER_SDP_QUEUE_CONNECTOR_DEVICE


def test_pointing_offsets(tango_context):
    """This test verifies sdp queue connector pointing cal attribute"""

    # pointing_cal = [scanID, cross_elevation_offset, elevation_offset ]
    POINTING_CAL_SKA001 = [1.0, 2.0, 3.0]
    POINTING_CAL_SKA002 = [4.0, 5.0, 6.0]
    POINTING_CAL_SKA003 = [7.0, 8.0, 9.0]
    POINTING_CAL_SKA004 = [10.0, 11.0, 12.0]

    dev_factory = DevFactory()
    sdp_queue_connector_device = dev_factory.get_device(
        HELPER_SDP_QUEUE_CONNECTOR_DEVICE
    )

    # Raise event on pointing_cal_SKA001 attribute
    sdp_queue_connector_device.set_pointing_cal_ska001(POINTING_CAL_SKA001)

    # Raise event on pointing_cal_SKA002 attribute
    sdp_queue_connector_device.set_pointing_cal_ska002(POINTING_CAL_SKA002)

    # Raise event on pointing_cal_SKA003 attribute
    sdp_queue_connector_device.set_pointing_cal_ska003(POINTING_CAL_SKA003)

    # Raise event on pointing_cal_SKA004 attribute
    sdp_queue_connector_device.set_pointing_cal_ska004(POINTING_CAL_SKA004)

    # Validate the values
    assert numpy.array_equal(
        sdp_queue_connector_device.pointing_cal_SKA001, POINTING_CAL_SKA001
    )
    assert numpy.array_equal(
        sdp_queue_connector_device.pointing_cal_SKA002, POINTING_CAL_SKA002
    )
    assert numpy.array_equal(
        sdp_queue_connector_device.pointing_cal_SKA003, POINTING_CAL_SKA003
    )
    assert numpy.array_equal(
        sdp_queue_connector_device.pointing_cal_SKA004, POINTING_CAL_SKA004
    )
