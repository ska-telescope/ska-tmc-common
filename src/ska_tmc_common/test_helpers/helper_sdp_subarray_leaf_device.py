"""
This module implements the Helper devices for subarray leaf nodes for testing
an integrated TMC
"""
# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument
import threading
import time
from enum import IntEnum
from typing import List, Tuple

import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from tango import AttrWriteType, EnsureOmniThread
from tango.server import attribute, command, run

from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice
from ska_tmc_common.test_helpers.helper_subarray_leaf_device import (
    HelperSubarrayLeafDevice,
)


class HelperSdpSubarrayLeafDevice(HelperSubarrayLeafDevice):
    """A device exposing commands and attributes of the CSP Subarray Leaf Nodes devices."""

    class InitCommand(HelperBaseDevice.InitCommand):
        """A class for the HelperSubarrayDevice's init_device() "command"."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            """
            super().do()
            self._device.set_change_event("sdpSubarrayObsState", True, False)
            return ResultCode.OK, ""

    sdpSubarrayObsState = attribute(
        dtype=ObsState,
        access=AttrWriteType.READ,
    )

    def init_device(self):
        super().init_device()
        self._obs_state = ObsState.EMPTY

    def read_sdpSubarrayObsState(self):
        """Reads the current observation state of the SDP subarray"""
        return self._obs_state

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format consists of receptorIDList.",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def AssignResources(
        self, argin: str = ""
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes AssignResources command on csp subarray devices
        """
        if self._defective:
            self._obs_state = ObsState.RESOURCING
            self.push_change_event("sdpSubarrayObsState", self._obs_state)
            return [ResultCode.FAILED], [
                "Device is Defective, cannot process command completely."
            ]

        if self._raise_exception:
            self._obs_state = ObsState.RESOURCING
            self.push_change_event("sdpSubarrayObsState", self._obs_state)
            self.thread = threading.Thread(
                target=self.wait_and_update_exception, args=["AssignResources"]
            )
            self.thread.start()

        elif self._obs_state != ObsState.IDLE:
            self._obs_state = ObsState.RESOURCING
            self.push_change_event("sdpSubarrayObsState", self._obs_state)
            thread = threading.Thread(
                target=self.update_device_obsstate, args=[ObsState.IDLE]
            )
            thread.start()
        return [ResultCode.OK], [""]

    def wait_and_update_exception(self, command_name):
        """Waits for 5 secs before pushing a longRunningCommandResult event."""
        with EnsureOmniThread():
            time.sleep(5)
            command_id = f"1000_{command_name}"
            command_result = (
                command_id,
                f"Exception occurred on device: {self.get_name()}",
            )
            self.push_change_event("longRunningCommandResult", command_result)

    def update_device_obsstate(self, value: IntEnum) -> None:
        """Updates the given data after a delay."""
        with tango.EnsureOmniThread():
            time.sleep(self._delay)
            self._obs_state = value
            time.sleep(0.1)
            self.push_change_event("obsState", self._obs_state)

    @command(
        dtype_in=int,
        doc_in="Set ObsState",
    )
    def SetDirectObsState(self, argin: ObsState) -> None:
        """
        Trigger a ObsState change
        """
        # import debugpy; debugpy.debug_this_thread()
        value = ObsState(argin)
        if self._obs_state != value:
            self._obs_state = value
            self.push_change_event("obsState", self._obs_state)


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
