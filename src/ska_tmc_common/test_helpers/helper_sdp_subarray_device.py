"""
This module implements the Helper devices for SdpSubarray device for testing
an integrated TMC
"""
# pylint: disable=attribute-defined-outside-init
import json
from typing import List, Tuple

import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from tango.server import command, run

from ska_tmc_common.test_helpers.helper_subarray_device import (
    HelperSubArrayDevice,
)


class HelperSdpSubArrayDevice(HelperSubArrayDevice):
    """A mock Sdp subarray device for triggering state changes with a command."""

    def is_AssignResources_allowed(self) -> bool:
        """
        Check if command `AssignResources` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format consists of receptorIDList.",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def AssignResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes AssignResources command on SdpSubarray devices
        """
        self.logger.info("Argin on SdpSubarray helper: %s", argin)
        input = json.loads(argin)

        if self._defective:
            self._obs_state = ObsState.RESOURCING
            self.push_change_event("obsState", self._obs_state)
            return [ResultCode.FAILED], [
                "Device is Defective, cannot process command completely."
            ]

        if "eb_id" not in input["execution_block"]:
            self.logger.info("eb_id is not present in Assign input json")
            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "eb_id not found in the input json string",
                "SdpSubarry.AssignResources",
                tango.ErrSeverity.ERR,
            )

        if self._obs_state != ObsState.IDLE:
            self._obs_state = ObsState.IDLE
            self.push_change_event("obsState", self._obs_state)

        return [ResultCode.OK], [
            "AssignResources invoked successfully on SDP SA"
        ]


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """
    Runs the HelperSubArrayDevice Tango device.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: integer. Exit code of the run method.
    """
    return run((HelperSubArrayDevice,), args=args, **kwargs)


if __name__ == "__main__":
    main()
