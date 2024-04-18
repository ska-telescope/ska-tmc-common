"""
This module defines a helper device that acts as SDP
Queue Connector in testing.
"""

from tango import ArgType, AttrDataFormat, AttrWriteType
from tango.server import attribute, command, run

from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice


# pylint: disable=invalid-name
class HelperSdpQueueConnector(HelperBaseDevice):
    """A helper device that emulates the behavior of pointing_cal_{dish_id}
    attributes from SdpQueueConnector device for testing.
    Queue Connector is a tango device of SDP.
    """

    def init_device(self):
        super().init_device()
        for i in range(1, 5):
            pointing_cal_name = f"pointing_cal_SKA{i:03}"
            setattr(self, f"_pointing_cal_ska{i:03}", [0.0, 0.0, 0.0])
            self.set_change_event(pointing_cal_name, True, False)

    @attribute(
        dtype=ArgType.DevDouble,
        dformat=AttrDataFormat.SPECTRUM,
        access=AttrWriteType.READ,
        max_dim_x=3,
    )
    def pointing_cal_SKA001(self) -> list[float]:
        """Attribute to give calibrated pointing offsets of dish
        SKA001"""
        return self._pointing_cal_ska001

    @attribute(
        dtype=ArgType.DevDouble,
        dformat=AttrDataFormat.SPECTRUM,
        access=AttrWriteType.READ,
        max_dim_x=3,
    )
    def pointing_cal_SKA002(self) -> list[float]:
        """Attribute to give calibrated pointing offsets of dish
        SKA002"""
        return self._pointing_cal_ska002

    @attribute(
        dtype=ArgType.DevDouble,
        dformat=AttrDataFormat.SPECTRUM,
        access=AttrWriteType.READ,
        max_dim_x=3,
    )
    def pointing_cal_SKA003(self) -> list[float]:
        """Attribute to give calibrated pointing offsets of dish
        SKA003"""
        return self._pointing_cal_ska003

    @attribute(
        dtype=ArgType.DevDouble,
        dformat=AttrDataFormat.SPECTRUM,
        access=AttrWriteType.READ,
        max_dim_x=3,
    )
    def pointing_cal_SKA004(self) -> list[float]:
        """Attribute to give calibrated pointing offsets of dish
        SKA004"""
        return self._pointing_cal_ska004

    @command(
        dtype_in=ArgType.DevDouble,
        dformat_in=AttrDataFormat.SPECTRUM,
        doc_in="([scanID, cross_elevation_offsets, elevation_offsets])",
    )
    def SetPointingCalSKA001(self, pointing_cal: list) -> None:
        """This method sets the value of pointing_cal_ska001 attribute also
        push the event for the attribute"""
        # pylint:disable = attribute-defined-outside-init
        self._pointing_cal_ska001 = pointing_cal
        self.push_change_event(
            "pointing_cal_ska001", self._pointing_cal_ska001
        )
        self.logger.info(
            "pointing_cal_ska001 attribute value updated to %s", pointing_cal
        )

    @command(
        dtype_in=ArgType.DevDouble,
        dformat_in=AttrDataFormat.SPECTRUM,
        doc_in="([scanID, cross_elevation_offsets, elevation_offsets])",
    )
    def SetPointingCalSKA002(self, pointing_cal: list) -> None:
        """This method sets the value of pointing_cal_ska002 attribute also
        push the event for the attribute"""
        # pylint:disable = attribute-defined-outside-init
        self._pointing_cal_ska002 = pointing_cal
        self.push_change_event(
            "pointing_cal_ska002", self._pointing_cal_ska002
        )
        self.logger.info(
            "pointing_cal_ska002 attribute value updated to %s", pointing_cal
        )

    @command(
        dtype_in=ArgType.DevDouble,
        dformat_in=AttrDataFormat.SPECTRUM,
        doc_in="([scanID, cross_elevation_offsets, elevation_offsets])",
    )
    def SetPointingCalSKA003(self, pointing_cal: list) -> None:
        """This method sets the value of pointing_cal_ska003 attribute also
        push the event for the attribute"""
        # pylint:disable = attribute-defined-outside-init
        self._pointing_cal_ska003 = pointing_cal
        self.push_change_event(
            "pointing_cal_ska003", self._pointing_cal_ska003
        )
        self.logger.info(
            "pointing_cal_ska003 attribute value updated to %s", pointing_cal
        )

    @command(
        dtype_in=ArgType.DevDouble,
        dformat_in=AttrDataFormat.SPECTRUM,
        doc_in="([scanID, cross_elevation_offsets, elevation_offsets])",
    )
    def SetPointingCalSKA004(self, pointing_cal: list) -> None:
        """This method sets the value of pointing_cal_ska004 attribute also
        push the event for the attribute"""
        # pylint:disable = attribute-defined-outside-init
        self._pointing_cal_ska004 = pointing_cal
        self.push_change_event(
            "pointing_cal_ska004", self._pointing_cal_ska004
        )
        self.logger.info(
            "pointing_cal_ska004 attribute value updated to %s", pointing_cal
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
