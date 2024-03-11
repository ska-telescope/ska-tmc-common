"""
This module implements the Helper Mccs subarray device
"""
import json

# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument
import threading
import time
from typing import List, Tuple

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState

from ska_tmc_common import FaultType
from ska_tmc_common.test_helpers.helper_subarray_device import (
    HelperSubArrayDevice,
)


class HelperMccsSubarrayDevice(HelperSubArrayDevice):
    """
    A device exposing commands and attributes of the Mccs Subarray Device.
    """

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
        "target_obsstates": [ObsState.RESOURCING, ObsState.EMPTY],
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

        - STUCK_IN_OBS_STATE:
          This fault type represents a scenario where the
          device gets stuck in a transitional obsstate as there is
          some failure. It also raise exception of the same.

        - COMMAND_NOT_ALLOWED:
          This fault type represents a situation where the
          given command is not allowed to be executed due to some
          authorization or permission issues. The device
          should respond with an appropriate error code and message.

        :raises: None
        """
        self.logger.info("Inducing fault for command %s", command_name)
        fault_type = self.defective_params["fault_type"]
        result = self.defective_params["result"]
        fault_message = self.defective_params["error_message"]

        if self.defective_params.get("intermediate_state"):
            intermediate_state = self.defective_params.get(
                "intermediate_state"
            )
        else:
            intermediate_state = ObsState.RESOURCING
            self.logger.info("intermediate_state is: %s", intermediate_state)

        if fault_type == FaultType.FAILED_RESULT:
            self.logger.info("FAILED RESULT Fault type")
            self.logger.info(
                "Target obsStates are: %s",
                self.defective_params.get("target_obsstates"),
            )
            if "target_obsstates" in self.defective_params.keys():
                # Utilise target_obsstate parameter when Subarray should
                # transition to specific obsState while returning
                # ResultCode.FAILED
                obsstate_list = self.defective_params.get("target_obsstates")
                for obsstate in obsstate_list:
                    self._obs_state = obsstate
                    time.sleep(1)
                    self.logger.info(
                        "Pushing target obsstate %s event", self._obs_state
                    )
                    self.push_change_event("obsState", self._obs_state)

                command_id = f"1000_{command_name}"
                command_result = (
                    command_id,
                    json.dumps(
                        [
                            ResultCode.FAILED,
                            f"Exception occured on device: {self.get_name()}",
                        ]
                    ),
                )
                self.logger.info(
                    "Pushing longRunningCommandResult %s event", command_result
                )
                self.push_change_event(
                    "longRunningCommandResult", command_result
                )
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
            self.logger.info("Pushing obsState %s event", intermediate_state)
            self.push_change_event("obsState", intermediate_state)
            return [ResultCode.QUEUED], [""]

        if fault_type == FaultType.STUCK_IN_OBSTATE:
            self._obs_state = intermediate_state
            self.logger.info("pushing obsState %s event", intermediate_state)
            self.push_change_event("obsState", intermediate_state)

            command_id = f"1000_{command_name}"
            command_result = (
                command_id,
                json.dumps(
                    [
                        ResultCode.FAILED,
                        f"Exception occured on device: {self.get_name()}",
                    ]
                ),
            )
            self.logger.info(
                "Pushing longRunningCommandResult %s event", command_result
            )
            self.push_change_event("longRunningCommandResult", command_result)
            return [ResultCode.QUEUED], [""]

        return [ResultCode.OK], [""]
