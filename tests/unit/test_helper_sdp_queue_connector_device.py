import ast

import msgpack
import msgpack_numpy
import numpy as np
import pytest

from ska_tmc_common import DevFactory
from tests.settings import HELPER_SDP_QUEUE_CONNECTOR_DEVICE


@pytest.mark.R1
def test_pointing_offsets(tango_context):
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
    dev_factory = DevFactory()
    sdp_subarray_device = dev_factory.get_device(
        HELPER_SDP_QUEUE_CONNECTOR_DEVICE
    )
    pack = msgpack.packb(POINTING_OFFSETS, default=msgpack_numpy.encode)
    sdp_subarray_device.SetDirectPointingOffsets(str(pack))
    encoded_string = sdp_subarray_device.pointing_offsets
    unpack = msgpack.unpackb(
        ast.literal_eval(encoded_string), object_hook=msgpack_numpy.decode
    )
    comparison = unpack == POINTING_OFFSETS
    assert comparison.all()
