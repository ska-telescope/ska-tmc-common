"""
This module defines a helper device that acts as SDP
Queue Connector in our testing.
"""

import logging

from tango import AttrWriteType, CmdArgType
from tango.server import Device, attribute, command

logger = logging.getLogger(__name__)


class HelperSdpQueueConnector(Device):
    """A helper SdpSubarray device intended to provide pointing
    offsets data from  Science Data Processor (SDP).
    It can be used to mock SdpQueueConnector's bahavior to test data
    which is coming from exposed pointing_offsets attribute."""

    def init_device(self):
        super().init_device()
        self._pointing_offsets = ("msgpack_numpy", b"")
        self.set_change_event("pointing_offsets", True, False)

    @attribute(
        dtype=CmdArgType.DevEncoded,
        access=AttrWriteType.READ,
    )
    def pointing_offsets(self) -> tuple[str, bytes]:
        """This method is used to read the attribute value for
        pointing_offsets from QueueConnector SDP device.
        The string contains a numpy ndarray in encoded
        byte form with below values in each array:
        [
        "Antenna_Name,"
        "CrossElevation_Offset,CrossElevation_Offset_Std,"
        "Elevation_Offset,Elevation_Offset_Std,"
        "Expected_Width_H,Expected_Width_V,"
        "Fitted_Width_H,Fitted_Width_H_Std,"
        "Fitted_Width_V,Fitted_Width_V_Std,"
        "Fitted_Height,Fitted_Height_Std"
        ]
        """
        return self._pointing_offsets

    @command(
        dtype_in=CmdArgType.DevEncoded,
        doc_in="Set pointing offsets",
    )
    def SetDirectPointingOffsets(
        self, pointing_offsets_data
    ) -> CmdArgType.DevVoid:
        """This method is used to write the attribute value for
        pointing_offsets for testing purpose.
        :param pointing_offsets_data: The variable contains a
        string which holds a numpy ndarray in encoded byte form
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
        self._pointing_offsets = pointing_offsets_data
        self.push_change_event(
            "pointing_offsets",
            self._pointing_offsets[0],
            self._pointing_offsets[1],
        )
        logger.info(
            "Received pointing offsets data is: %s", self._pointing_offsets
        )
