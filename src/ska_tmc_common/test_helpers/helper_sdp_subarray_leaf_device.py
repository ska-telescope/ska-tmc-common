"""
This module implements the Helper devices for subarray leaf nodes for testing
an integrated TMC
"""
import json
import threading

# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument
from typing import List, Tuple

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from tango import AttrWriteType
from tango.server import attribute, command, run

from ska_tmc_common import FaultType
from ska_tmc_common.test_helpers.helper_subarray_leaf_device import (
    HelperSubarrayLeafDevice,
)


class HelperSdpSubarrayLeafDevice(HelperSubarrayLeafDevice):
    """A device exposing commands and attributes of the CSP Subarray Leaf
    Nodes devices."""

    def init_device(self) -> None:
        super().init_device()
        self.dev_name = self.get_name()
        self._isSubsystemAvailable = False
        self._raise_exception = False
        self._defective = json.dumps(
            {
                "enabled": False,
                "fault_type": FaultType.FAILED_RESULT,
                "error_message": "Default exception.",
                "result": ResultCode.FAILED,
            }
        )
        self.defective_params = json.loads(self._defective)
        self._pointing_calibrations = []

    class InitCommand(HelperSubarrayLeafDevice.InitCommand):
        """A class for the HelperSubarrayDevice's init_device() "command"."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            """
            super().do()
            self._device.set_change_event("sdpSubarrayObsState", True, False)
            self._device.set_change_event("pointingCalibrations", True, False)
            return ResultCode.OK, ""

    sdpSubarrayObsState = attribute(
        dtype=ObsState,
        access=AttrWriteType.READ,
    )

    pointingCalibrations = attribute(
        dtype="DevString",
        access=AttrWriteType.READ,
    )

    def read_sdpSubarrayObsState(self):
        """Reads the current observation state of the SDP subarray"""
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

    def read_pointingCalibrations(self):
        """Reads the current pointing offsets of the SDP subarray"""
        return json.dumps(self._pointing_calibrations)
    
    @command(
            dtype_in="DevString",
            doc_in="Set the pointing calibrations"

    )
    def SetDirectPointingCalibrations(self, pointing_calibrations: str):
        """
        Manual trigger to change the pointing calibrations
        """
        self._pointing_calibrations = json.loads(pointing_calibrations)
        self.push_change_event("pointingCalibrations", json.dumps(self._pointing_calibrations))
        self.logger.info("Updated Pointing offsets are: %s", self._pointing_calibrations)


    def push_obs_state_event(self, obs_state: ObsState) -> None:
        self.logger.info(
            "Pushing change event for SdpSubarrayObsState: %s", obs_state
        )
        self.push_change_event("sdpSubarrayObsState", obs_state)

    def induce_fault(
        self,
        command_name: str,
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        Induces a fault into the device based on the given parameters.

        :param command_name: The name of the
         command for which a fault is being induced.
        :type command_name: str

        :param dtype: The data type of the fault parameter.
        :type dtype: str

        :param rtype: A tuple containing two lists - the
         list of possible result codes and the list of error messages.
        :type rtype: Tuple[List[ResultCode], List[str]]

        Example:
        defective = json.dumps(
        {
        "enabled": False,
        "fault_type": FaultType.FAILED_RESULT,
        "error_message": "Default exception.",
        "result": ResultCode.FAILED,
        }
        )
        defective_params = json.loads(defective)

        Detailed Explanation:
        This method simulates inducing various types of faults into a device
        to test its robustness and error-handling capabilities.

        - FAILED_RESULT:
          A fault type that triggers a failed result code
          for the command. The device will return a result code of 'FAILED'
          along with a custom error message, indicating that
          the command execution has failed.

        - LONG_RUNNING_EXCEPTION:
          A fault type that simulates a command getting stuck in an
          intermediate state for an extended period.
          This could simulate a situation where a command execution
          hangs due to some internal processing issue.

        - STUCK_IN_INTERMEDIATE_STATE:
          This fault type represents a scenario where the
          device gets stuck in an intermediate state between two
          well-defined states. This can help test the device's state
          recovery and error handling mechanisms.

        - COMMAND_NOT_ALLOWED:
          This fault type represents a situation where the
          given command is not allowed to be executed due to some
          authorization or permission issues. The device
          should respond with an appropriate error code and message.

        :raises: None
        """
        fault_type = self.defective_params["fault_type"]
        result = self.defective_params["result"]
        fault_message = self.defective_params["error_message"]
        intermediate_state = (
            self.defective_params.get("intermediate_state")
            or ObsState.RESOURCING
        )

        if fault_type == FaultType.FAILED_RESULT:
            return [result], [fault_message]

        if fault_type == FaultType.LONG_RUNNING_EXCEPTION:
            thread = threading.Timer(
                self._delay,
                function=self.push_command_result,
                args=[result, command_name, fault_message],
            )
            thread.start()
            return [ResultCode.QUEUED], [""]

        if fault_type == FaultType.STUCK_IN_INTERMEDIATE_STATE:
            self._obs_state = intermediate_state
            self.push_obs_state_event(intermediate_state)
            return [ResultCode.QUEUED], [""]

        return [ResultCode.OK], [""]


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
