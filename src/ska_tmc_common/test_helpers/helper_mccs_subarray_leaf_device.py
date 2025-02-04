"""
This module implements the Helper devices for MCCS subarray leaf nodes
for testing an integrated TMC
"""

# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument
from typing import Tuple

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import AdminMode
from tango import AttrWriteType
from tango.server import attribute, command, run

from ska_tmc_common.test_helpers.helper_subarray_leaf_device import (
    HelperSubarrayLeafDevice,
)


# pylint: disable=invalid-name
class HelperMccsSubarrayLeafDevice(HelperSubarrayLeafDevice):
    """A device exposing commands and attributes of the MCCS Subarray Leaf
    Node devices."""

    def init_device(self) -> None:
        super().init_device()
        self._mccs_subarray_admin_mode: AdminMode = AdminMode.OFFLINE

    class InitCommand(HelperSubarrayLeafDevice.InitCommand):
        """A class for the HelperSubarrayDevice's init_device() "command"."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            :return: ResultCode and message
            """
            super().do()
            self._device.set_change_event("mccsSubarrayAdminMode", True, False)
            return ResultCode.OK, ""

    mccsSubarrayAdminMode = attribute(
        dtype=AdminMode,
        access=AttrWriteType.READ,
    )

    def read_mccsSubarrayAdminMode(self):
        """
        Reads the current admin mode of the CSP subarray
        :return: obs state
        """
        return self._mccs_subarray_admin_mode

    @command(
        dtype_in=int,
        doc_in="Set AdminMode",
    )
    def SetMccsSubarrayLeafNodeAdminMode(self, argin: int) -> None:
        """
        Trigger a admin mode change
        """
        value = AdminMode(argin)
        if self._mccs_subarray_admin_mode != value:
            self._mccs_subarray_admin_mode = value
            self.push_change_event(
                "mccsSubarrayAdminMode", self._mccs_subarray_admin_mode
            )


def main(args=None, **kwargs):
    """
    Runs the HelperSubarrayLeafDevice Tango device.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: integer. Exit code of the run method.
    """
    return run((HelperMccsSubarrayLeafDevice,), args=args, **kwargs)


if __name__ == "__main__":
    main()
