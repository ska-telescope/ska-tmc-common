"""
This module implements the Helper Mccs subarray device
"""

import threading
import time

# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument
from typing import List, Tuple

from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode
from tango.server import command, run

from ska_tmc_common.test_helpers.constants import RELEASE_RESOURCES
from ska_tmc_common.test_helpers.helper_subarray_device import (
    HelperSubArrayDevice,
)


class HelperMccsSubarrayDevice(HelperSubArrayDevice):
    """
    A device exposing commands and attributes of the Mccs Subarray Device.
    """

    @command(
        dtype_in="str",
        doc_in="The input string in JSON format consists of receptorIDList.",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ReleaseResources(self, argin) -> Tuple[List[ResultCode], List[str]]:
        """
        This method simulates ReleaseResources command on MCCS subarray device
        :return: ResultCode and message
        """
        command_id = f"{time.time()}_ReleaseResources"
        self.logger.info(
            "Instructed simulator to invoke ReleaseResources command"
        )
        self.logger.info(argin)
        self.update_command_info(RELEASE_RESOURCES, "")

        # AdminMode check
        proceed, result, message = self._check_if_admin_mode_offline(
            "ReleaseResources"
        )
        if not proceed:
            return result, message

        if self.defective_params["enabled"]:
            return self.induce_fault("ReleaseResources", command_id)

        self.update_device_obsstate(ObsState.RESOURCING, RELEASE_RESOURCES)
        thread = threading.Timer(
            self._delay,
            self.update_device_obsstate,
            args=[ObsState.EMPTY, RELEASE_RESOURCES],
        )
        thread.start()
        thread = threading.Timer(
            self._delay,
            self.push_command_result,
            args=[ResultCode.OK, RELEASE_RESOURCES],
            kwargs={"command_id": command_id},
        )
        thread.start()
        self.logger.debug(
            "ReleaseResources command invoked, obsState will transition to"
            + "IDLE, current obsState is %s",
            self._obs_state,
        )
        return [ResultCode.QUEUED], [command_id]


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """
    Runs the HelperMccsSubarrayDevice Tango device.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: integer. Exit code of the run method.
    """
    return run((HelperMccsSubarrayDevice,), args=args, **kwargs)


if __name__ == "__main__":
    main()
