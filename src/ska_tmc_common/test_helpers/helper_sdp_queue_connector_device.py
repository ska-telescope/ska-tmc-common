"""
This module defines a helper device that acts as SDP
Queue Connector in testing.
"""

import logging

from tango import AttrWriteType, CmdArgType
from tango.server import Device, attribute, command, run

logger = logging.getLogger(__name__)


# pylint: disable=invalid-name
class HelperSdpQueueConnector(Device):
    """A helper device that emulates the behavior of pointing_offsets attribute
    from SdpQueueConnector device for testing.
    Queue Connector is a tango device of SDP.
    """

    def init_device(self):
        super().init_device()
        # The 0th index is a placeholder and the data at
        # index 1 is in byte format
        self._pointing_offsets = ("msgpack_numpy", b"")
        self.set_change_event("pointing_offsets", True, False)

    @attribute(
        dtype=CmdArgType.DevEncoded,
        access=AttrWriteType.READ,
    )
    def pointing_offsets(self) -> tuple[str, bytes]:
        """Returns the attribute value for
        pointing_offsets from QueueConnector SDP device.
        The returned tuple contains a string literal msgpack_numpy
        and a numpy ndarray in encoded byte form with
        below values in each array:
        [
        "Antenna_Name,"
        "CrossElevation_Offset,CrossElevation_Offset_Std,"
        "Elevation_Offset,Elevation_Offset_Std,"
        "Expected_Width_H,Expected_Width_V,"
        "Fitted_Width_H,Fitted_Width_H_Std,"
        "Fitted_Width_V,Fitted_Width_V_Std,"
        "Fitted_Height,Fitted_Height_Std"
        ]
        :return: the attribute value for
        pointing_offsets from QueueConnector SDP device
        """
        return self._pointing_offsets

    @command(
        dtype_in=CmdArgType.DevEncoded,
        doc_in="Set pointing offsets",
    )
    def SetDirectPointingOffsets(
        self, pointing_offsets_data
    ) -> CmdArgType.DevVoid:
        """Sets the attribute value for pointing_offsets for testing purposes.
        :param pointing_offsets_data: The variable contains a string literal
        msgpack_numpy and a numpy ndarray in encoded byte form
        with below values in each array:
        [
        Antenna_Name,
        CrossElevation_Offset,CrossElevation_Offset_Std,
        Elevation_Offset,Elevation_Offset_Std,
        Expected_Width_H,Expected_Width_VFitted_Width_H,
        Fitted_Width_H_Std,Fitted_Width_V,Fitted_Width_V_Std,
        Fitted_Height,Fitted_Height_Std
        ]
        """
        # pylint: disable=attribute-defined-outside-init
        self._pointing_offsets = pointing_offsets_data
        # Below syntax is as per the pytango docs for DevEncoded data type
        # Syntax: push_change_event(self, attr_name, str_data, data)
        self.push_change_event(
            "pointing_offsets",
            self._pointing_offsets[0],
            self._pointing_offsets[1],
        )
        logger.info(
            "Received pointing offsets data is: %s", self._pointing_offsets
        )


def main(args=None, **kwargs):
    """
    Runs the HelperSdpQueueConnector Tango device.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: integer. Exit code of the run method.
    """
    return run((HelperSdpQueueConnector,), args=args, **kwargs)


if __name__ == "__main__":
    main()
