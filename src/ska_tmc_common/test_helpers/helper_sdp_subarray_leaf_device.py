"""
This module implements the Helper devices for subarray leaf nodes for testing
an integrated TMC
"""

# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument
from typing import Tuple

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from tango import AttrWriteType
from tango.server import attribute, command, run

from ska_tmc_common.test_helpers.helper_subarray_leaf_device import (
    HelperSubarrayLeafDevice,
)


# pylint: disable=invalid-name
class HelperSdpSubarrayLeafDevice(HelperSubarrayLeafDevice):
    """A device exposing commands and attributes of the CSP Subarray Leaf
    Nodes devices."""

    def init_device(self) -> None:
        super().init_device()
        self.dev_name = self.get_name()
        self._isSubsystemAvailable = False
        self._raise_exception = False

    class InitCommand(HelperSubarrayLeafDevice.InitCommand):
        """A class for the HelperSubarrayDevice's init_device() "command"."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            :return: ResultCode and message
            """
            super().do()
            self._device.set_change_event("sdpSubarrayObsState", True, False)
            return ResultCode.OK, ""

    sdpSubarrayObsState = attribute(
        dtype=ObsState,
        access=AttrWriteType.READ,
    )

    def read_sdpSubarrayObsState(self):
        """
        Reads the current observation state of the SDP subarray
        :return: obsstate value
        """
        return self._obs_state

    @command(
        dtype_in=int,
        doc_in="Set ObsState",
    )
    def SetSdpSubarrayLeafNodeObsState(self, argin: ObsState) -> None:
        """
        Trigger a ObsState change
        """
        value = ObsState(argin)
        if self._obs_state != value:
            self._obs_state = value
            self.push_change_event("sdpSubarrayObsState", self._obs_state)

    def push_obs_state_event(self, obs_state: ObsState) -> None:
        self.logger.info(
            "Pushing change event for SdpSubarrayObsState: %s", obs_state
        )
        self.push_change_event("sdpSubarrayObsState", obs_state)


def main(args=None, **kwargs):
    """
    Runs the HelperSubarrayLeafDevice Tango device.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: integer. Exit code of the run method.
    """
    return run((HelperSdpSubarrayLeafDevice,), args=args, **kwargs)


if __name__ == "__main__":
    main()
