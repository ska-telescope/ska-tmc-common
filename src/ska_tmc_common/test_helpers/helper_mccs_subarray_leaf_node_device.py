"""
This module contains the implementation of the HelperMccsSubarrayLeafNode class
which exposes commands and attributes of the Mccs Subarray Leaf Node devices.
"""
import threading
import time
from typing import List, Tuple

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from tango import EnsureOmniThread
from tango.server import command

from ska_tmc_common.test_helpers.helper_subarray_leaf_device import (
    HelperSubarrayLeafDevice,
)

from .constants import RESTART


class HelperMccsSubarrayLeafNode(HelperSubarrayLeafDevice):
    """
    A device exposing commands and attributes of the Mccs Subarray Leaf Node
    devices.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._obs_state = ObsState.EMPTY

    def wait_and_update_command_result(self, command_name):
        """Waits for 5 secs before pushing a longRunningCommandResult event."""
        with EnsureOmniThread():
            time.sleep(5)
            command_id = f"1000_{command_name}"
            command_result = (
                command_id,
                str([ResultCode.OK, f"command {command_name} completed"]),
            )
            self.push_change_event("longRunningCommandResult", command_result)

    @command(
        dtype_in=int,
        dtype_out="DevVarLongStringArray",
        doc_in="integer argument(subarray_id) for Restart command.",
        doc_out="(ReturnType, 'informational message')",
    )
    def Restart(self, argin: int) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes the Restart command on subarray devices.

        :param argin: integer argument(subarray_id) for Restart command.
        :return: Tuple containing ResultCode and informational message.
        :rtype: tuple
        """
        self.logger.info("Instructed Mccs Subarray to invoke Restart command")
        self.update_command_info(RESTART, "")
        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault("Restart")

        if self._obs_state != ObsState.EMPTY:
            self._obs_state = ObsState.RESTARTING
            self.push_change_event("obsState", self._obs_state)

            command_result_thread = threading.Thread(
                target=self.wait_and_update_command_result, args=["Restart"]
            )
            command_result_thread.start()

            thread = threading.Thread(
                target=self.update_device_obsstate,
                args=[ObsState.EMPTY, RESTART],
            )
            thread.start()

        self.logger.info("Restart command completed.")
        return [ResultCode.OK], ["Restart command executed successfully."]
