import msgpack
import msgpack_numpy
import numpy
import numpy as np

from ska_tmc_common import DevFactory
from tests.settings import HELPER_SDP_QUEUE_CONNECTOR_DEVICE

POINTING_OFFSETS = np.array(
    [
        [
            "SKA001",
            -4.115211938625473,
            69.9725295732531,
            -7.090356031104502,
            104.10028693155607,
            70.1182176899719,
            78.8829949012184,
            95.49061976199042,
            729.5782881970024,
            119.27311545171803,
            1065.4074085647912,
            0.9948872678443994,
            0.8441090109163307,
        ],
        [
            "SKA003",
            -4.115211938625473,
            69.9725295732531,
            -7.090356031104502,
            104.10028693155607,
            70.1182176899719,
            78.8829949012184,
            95.49061976199042,
            729.5782881970024,
            119.27311545171803,
            1065.4074085647912,
            0.9948872678443994,
            0.8441090109163307,
        ],
    ]
)


def test_pointing_offsets(tango_context):
    dev_factory = DevFactory()
    sdp_queue_connector_device = dev_factory.get_device(
        HELPER_SDP_QUEUE_CONNECTOR_DEVICE
    )

    # Create an encoded data n byte form
    encoded_numpy_ndarray_in_byte_form = msgpack.packb(
        POINTING_OFFSETS, default=msgpack_numpy.encode
    )

    # Raise event on pointing_offsets attribute
    sdp_queue_connector_device.SetDirectPointingOffsets(
        ("msgpack_numpy", encoded_numpy_ndarray_in_byte_form)
    )

    # Store the data received on the pointing_offsets attribute
    encoded_numpy_ndarray_string_from_qc = (
        sdp_queue_connector_device.pointing_offsets
    )

    # Decode the data n byte form
    decoded_numpy_ndarray = msgpack.unpackb(
        encoded_numpy_ndarray_string_from_qc[1],
        object_hook=msgpack_numpy.decode,
    )
    assert numpy.array_equal(decoded_numpy_ndarray, POINTING_OFFSETS)
