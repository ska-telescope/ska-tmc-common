"""Helper device for MCCSSubarray device"""
from typing import Tuple

from ska_tango_base.commands import ResultCode
from ska_tango_base.subarray import SKASubarray
from tango import AttrWriteType, DevString
from tango.server import attribute

from ska_tmc_common import HelperSubArrayDevice

# pylint: disable=attribute-defined-outside-init


class HelperMccsSubarray(HelperSubArrayDevice):
    """A  helper MCCS Subarray device for triggering state changes with a
    command.
    """

    def init_device(self) -> None:
        super().init_device()
        self._scan_id = None
        self._assigned_resources = "{ }"

    class InitCommand(SKASubarray.InitCommand):
        """A class for the HelperMccsStateDevice's init_device() "command"."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            :returns: ResultCode, message
            :rtype:tuple
            """
            super().do()
            self._device.set_change_event("assignedResources", True, False)
            return (ResultCode.OK, "")

    scanId = attribute(dtype="DevLong", access=AttrWriteType.READ)

    @attribute(dtype="DevString")
    def assignedResources(self) -> DevString:
        return self._assigned_resources

    @assignedResources.write
    def assignedResources(self, assignResources: DevString = None) -> None:
        self._assigned_resources = assignResources

    def read_scanId(self) -> int:
        """This method is used to read the attribute value for scanId."""
        return self._scan_id
