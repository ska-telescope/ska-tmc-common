"""
This module implements the Helper devices for subarray leaf nodes for testing
an integrated TMC
"""

# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument
from typing import Tuple

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import AdminMode, ObsState
from tango import AttrWriteType
from tango.server import attribute, command, run

from ska_tmc_common.test_helpers.helper_subarray_leaf_device import (
    HelperSubarrayLeafDevice,
)


# pylint: disable=invalid-name
class HelperCspSubarrayLeafDevice(HelperSubarrayLeafDevice):
    """A device exposing commands and attributes of the CSP Subarray Leaf
    Node devices."""

    def init_device(self) -> None:
        super().init_device()
        self._isSubsystemAvailable = True
        self._isAdminModeEnabled: bool = False
        self._csp_subarray_admin_mode: AdminMode = AdminMode.OFFLINE

    class InitCommand(HelperSubarrayLeafDevice.InitCommand):
        """A class for the HelperSubarrayDevice's init_device() "command"."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            :return: ResultCode and message
            """
            super().do()
            self._device.set_change_event("cspSubarrayObsState", True, False)
            self._device.set_change_event("cspSubarrayAdminMode", True, False)
            return ResultCode.OK, ""

    cspSubarrayObsState = attribute(
        dtype=ObsState,
        access=AttrWriteType.READ,
    )
    cspSubarrayAdminMode = attribute(
        dtype=AdminMode,
        access=AttrWriteType.READ,
    )

    def read_cspSubarrayObsState(self):
        """
        Reads the current observation state of the CSP subarray
        :return: obs state
        """
        return self._obs_state

    def read_cspSubarrayAdminMode(self):
        """
        Reads the current observation state of the CSP subarray
        :return: obs state
        """
        return self._csp_subarray_admin_mode

    @command(
        dtype_in=int,
        doc_in="Set ObsState",
    )
    def SetCspSubarrayLeafNodeObsState(self, argin: int) -> None:
        """
        Trigger a ObsState change
        """
        value = ObsState(argin)
        if self._obs_state != value:
            self._obs_state = value
            self.push_change_event("cspSubarrayObsState", self._obs_state)

    @command(
        dtype_in=int,
        doc_in="Set AdminMode",
    )
    def SetCspSubarrayLeafNodeAdminMode(self, argin: int) -> None:
        """
        Trigger a ObsState change
        """
        value = AdminMode(argin)
        if self._csp_subarray_admin_mode != value:
            self._csp_subarray_admin_mode = value
            self.push_change_event(
                "cspSubarrayAdminMode", self._csp_subarray_admin_mode
            )

    def push_obs_state_event(self, obs_state: ObsState) -> None:
        self.logger.info(
            "Pushing change event for CspSubarrayObsState: %s", obs_state
        )
        self._obs_state = obs_state
        self.push_change_event("cspSubarrayObsState", obs_state)


def main(args=None, **kwargs):
    """
    Runs the HelperSubarrayLeafDevice Tango device.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: integer. Exit code of the run method.
    """
    return run((HelperCspSubarrayLeafDevice,), args=args, **kwargs)


if __name__ == "__main__":
    main()
