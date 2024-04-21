"""
This module defines a helper device that acts as SDP
Queue Connector in testing.
"""

from tango import ArgType, AttrDataFormat, AttrWriteType
from tango.server import attribute, command, run

from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice

DISH_DEVICE_LIST = [
    "SKA001",
    "SKA002",
    "SKA003",
    "SKA004",
    "SKA063",
    "SKA036",
    "SKA100",
]


# pylint: disable=invalid-name
class HelperSdpQueueConnector(HelperBaseDevice):
    """A helper device that emulates the behavior of pointing_cal_{dish_id}
    attributes from SdpQueueConnector device for testing.
    Queue Connector is a tango device of SDP.
    """

    def init_device(self):
        super().init_device()
        for dish_id in DISH_DEVICE_LIST:
            pointing_cal_name = f"pointing_cal_{dish_id}"
            setattr(self, f"_pointing_cal_{dish_id.lower()}", [0.0, 0.0, 0.0])
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

    @attribute(
        dtype=ArgType.DevDouble,
        dformat=AttrDataFormat.SPECTRUM,
        access=AttrWriteType.READ,
        max_dim_x=3,
    )
    def pointing_cal_SKA036(self) -> list[float]:
        """Attribute to give calibrated pointing offsets of dish
        SKA036"""
        return self._pointing_cal_ska036

    @attribute(
        dtype=ArgType.DevDouble,
        dformat=AttrDataFormat.SPECTRUM,
        access=AttrWriteType.READ,
        max_dim_x=3,
    )
    def pointing_cal_SKA063(self) -> list[float]:
        """Attribute to give calibrated pointing offsets of dish
        SKA063"""
        return self._pointing_cal_ska063

    @attribute(
        dtype=ArgType.DevDouble,
        dformat=AttrDataFormat.SPECTRUM,
        access=AttrWriteType.READ,
        max_dim_x=3,
    )
    def pointing_cal_SKA100(self) -> list[float]:
        """Attribute to give calibrated pointing offsets of dish
        SKA100"""
        return self._pointing_cal_ska100

    @command(
        dtype_in=ArgType.DevDouble,
        dformat_in=AttrDataFormat.SPECTRUM,
        doc_in="([scanID, cross_elevation_offsets, elevation_offsets])",
    )
    def SetPointingCalSka001(self, pointing_cal: list) -> None:
        """This method sets the value of pointing_cal_SKA001 attribute also
        push the event for the attribute"""
        # pylint:disable = attribute-defined-outside-init
        self._pointing_cal_ska001 = pointing_cal
        self.push_change_event("pointing_cal_SKA001", pointing_cal)
        self.logger.info(
            "pointing_cal_SKA001 attribute value updated to %s", pointing_cal
        )

    @command(
        dtype_in=ArgType.DevDouble,
        dformat_in=AttrDataFormat.SPECTRUM,
        doc_in="([scanID, cross_elevation_offsets, elevation_offsets])",
    )
    def SetPointingCalSka002(self, pointing_cal: list) -> None:
        """This method sets the value of pointing_cal_SKA002 attribute also
        push the event for the attribute"""
        # pylint:disable = attribute-defined-outside-init
        self._pointing_cal_ska002 = pointing_cal
        self.push_change_event(
            "pointing_cal_SKA002", self._pointing_cal_ska002
        )
        self.logger.info(
            "pointing_cal_SKA002 attribute value updated to %s", pointing_cal
        )

    @command(
        dtype_in=ArgType.DevDouble,
        dformat_in=AttrDataFormat.SPECTRUM,
        doc_in="([scanID, cross_elevation_offsets, elevation_offsets])",
    )
    def SetPointingCalSka003(self, pointing_cal: list) -> None:
        """This method sets the value of pointing_cal_SKA003 attribute also
        push the event for the attribute"""
        # pylint:disable = attribute-defined-outside-init
        self._pointing_cal_ska003 = pointing_cal
        self.push_change_event(
            "pointing_cal_SKA003", self._pointing_cal_ska003
        )
        self.logger.info(
            "pointing_cal_SKA003 attribute value updated to %s", pointing_cal
        )

    @command(
        dtype_in=ArgType.DevDouble,
        dformat_in=AttrDataFormat.SPECTRUM,
        doc_in="([scanID, cross_elevation_offsets, elevation_offsets])",
    )
    def SetPointingCalSka004(self, pointing_cal: list) -> None:
        """This method sets the value of pointing_cal_SKA004 attribute also
        push the event for the attribute"""
        # pylint:disable = attribute-defined-outside-init
        self._pointing_cal_ska004 = pointing_cal
        self.push_change_event(
            "pointing_cal_SKA004", self._pointing_cal_ska004
        )
        self.logger.info(
            "pointing_cal_SKA004 attribute value updated to %s", pointing_cal
        )

    @command(
        dtype_in=ArgType.DevDouble,
        dformat_in=AttrDataFormat.SPECTRUM,
        doc_in="([scanID, cross_elevation_offsets, elevation_offsets])",
    )
    def SetPointingCalSka036(self, pointing_cal: list) -> None:
        """This method sets the value of pointing_cal_SKA036 attribute also
        push the event for the attribute"""
        # pylint:disable = attribute-defined-outside-init
        self._pointing_cal_ska036 = pointing_cal
        self.push_change_event("pointing_cal_SKA036", pointing_cal)
        self.logger.info(
            "pointing_cal_SKA036 attribute value updated to %s", pointing_cal
        )

    @command(
        dtype_in=ArgType.DevDouble,
        dformat_in=AttrDataFormat.SPECTRUM,
        doc_in="([scanID, cross_elevation_offsets, elevation_offsets])",
    )
    def SetPointingCalSka063(self, pointing_cal: list) -> None:
        """This method sets the value of pointing_cal_SKA063 attribute also
        push the event for the attribute"""
        # pylint:disable = attribute-defined-outside-init
        self._pointing_cal_ska063 = pointing_cal
        self.push_change_event("pointing_cal_SKA063", pointing_cal)
        self.logger.info(
            "pointing_cal_SKA063 attribute value updated to %s", pointing_cal
        )

    @command(
        dtype_in=ArgType.DevDouble,
        dformat_in=AttrDataFormat.SPECTRUM,
        doc_in="([scanID, cross_elevation_offsets, elevation_offsets])",
    )
    def SetPointingCalSka100(self, pointing_cal: list) -> None:
        """This method sets the value of pointing_cal_SKA100 attribute also
        push the event for the attribute"""
        # pylint:disable = attribute-defined-outside-init
        self._pointing_cal_ska100 = pointing_cal
        self.push_change_event("pointing_cal_SKA100", pointing_cal)
        self.logger.info(
            "pointing_cal_SKA100 attribute value updated to %s", pointing_cal
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
