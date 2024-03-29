"""
This module implements the Helper MCCS controller devices for testing
an integrated TMC
"""
import json
import threading
import time
from typing import List, Tuple

# pylint: disable=unused-argument
import tango
from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from tango import EnsureOmniThread
from tango.server import command

from ska_tmc_common import CommandNotAllowed, DevFactory, FaultType
from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice

from .constants import ABORT, ALLOCATE, CONFIGURE, END, RELEASE, RESTART


# pylint: disable=attribute-defined-outside-init,invalid-name
class HelperMCCSController(HelperBaseDevice):
    """A helper MCCS controller device for triggering state changes
    with a command"""

    def init_device(self) -> None:
        super().init_device()
        self.dev_name = self.get_name()
        self._raise_exception = False
        self._command_delay_info = {
            CONFIGURE: 2,
            ABORT: 2,
            RESTART: 2,
            END: 2,
            ALLOCATE: 2,
            RELEASE: 2,
        }

    class InitCommand(SKABaseDevice.InitCommand):
        """A class for the HelperMCCSController's init_device() "command"."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            :return: ResultCode, message
            :rtype:tuple
            """
            super().do()
            return (ResultCode.OK, "")

    def induce_fault(
        self,
        command_name: str,
        command_id: str,
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        Induces a fault into the device based on the given parameters.

        :param command_name: The name of the
         command for which a fault is being induced.
        :type command_name: str
        :param command_id: command id
        :type command_id: str
        :return: ResultCode and command id
        :rtype: Tuple[List[ResultCode], List[str]]

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

          New method is explicitly introduced since MCCS Master Leaf Node
          does not have Obs State.

        :raises: None
        """
        fault_type = self.defective_params["fault_type"]
        result = self.defective_params["result"]
        fault_message = self.defective_params["error_message"]

        if fault_type == FaultType.FAILED_RESULT:
            return [result], [fault_message]

        if fault_type == FaultType.LONG_RUNNING_EXCEPTION:
            thread = threading.Timer(
                self._delay,
                function=self.push_command_result,
                args=[result, command_id, fault_message],
            )
            thread.start()
            return [ResultCode.QUEUED], [command_id]

        if fault_type == FaultType.STUCK_IN_INTERMEDIATE_STATE:
            return [ResultCode.QUEUED], [command_id]

        return [ResultCode.OK], [command_id]

    @command(
        dtype_in=str,
        doc_in="Set Defective parameters",
    )
    def SetDefective(self, values: str) -> None:
        """
        Trigger defective change
        :param: values
        :type: str
        """
        input_dict = json.loads(values)
        self.logger.info("Setting defective params to %s", input_dict)
        self.defective_params = input_dict

    @command(
        dtype_in=bool,
        doc_in="Raise Exception",
    )
    def SetRaiseException(self, value: bool) -> None:
        """Set Raise Exception"""
        self.logger.info("Setting the raise exception value to : %s", value)
        self._raise_exception = value

    def wait_and_update_exception(self, command_id):
        """Waits for 5 secs before pushing a longRunningCommandResult event."""
        with EnsureOmniThread():
            time.sleep(5)

            command_result = (
                command_id,
                json.dumps(
                    [
                        ResultCode.FAILED,
                        f"Exception occured on device: {self.get_name()}",
                    ]
                ),
            )
            self.logger.info("exception will be raised as %s", command_result)
            self.push_change_event("longRunningCommandResult", command_result)

    def update_lrcr(
        self, command_name: str = "", command_id: str = ""
    ) -> None:
        """Updates the longrunningcommandresult  after a delay."""
        delay_value = 0
        with tango.EnsureOmniThread():
            if command_name in self._command_delay_info:
                delay_value = self._command_delay_info[command_name]
            time.sleep(delay_value)
            self.logger.info(
                "Sleep %s for command %s ", delay_value, command_name
            )

        self.push_command_result(ResultCode.OK, command_id)

    def is_Allocate_allowed(self) -> bool:
        """
        Check if command `Allocate` is allowed in the current device
        state.

        :return: ``True`` if the command is allowed
        :rtype: bool
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("Allocate Command is allowed")
        return True

    @command(
        dtype_in="DevString",
        doc_in="JSON-encoded string with the resources to add to subarray",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Allocate(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes Allocate command on MCCS
        controller device

        :return: a tuple containing ResultCode and Message
        :rtype: Tuple
        """
        command_id = f"{time.time()}-Allocate"
        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault("Allocate", command_id)
        if self._raise_exception:
            self.logger.info("exception thread")
            thread = threading.Thread(
                target=self.wait_and_update_exception, args=[command_id]
            )
            thread.start()
            return [ResultCode.QUEUED], [command_id]

        argin_json = json.loads(argin)
        subarray_id = int(argin_json["subarray_id"])
        mccs_subarray_device_name = "low-mccs/subarray/" + f"{subarray_id:02}"
        dev_factory = DevFactory()
        mccs_subarray_proxy = dev_factory.get_device(mccs_subarray_device_name)
        mccs_subarray_proxy.AssignResources(argin)

        thread = threading.Thread(
            target=self.update_lrcr, args=["Allocate", command_id]
        )
        thread.start()
        self.logger.info("Allocate invoked on MCCS Controller")
        return [ResultCode.QUEUED], [command_id]

    def is_Release_allowed(self) -> bool:
        """
        Check if command `Release` is allowed in the current
        device state.

        :return: ``True`` if the command is allowed
        :rtype: bool
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        return True

    @command(
        dtype_in="DevString",
        doc_in="JSON-encoded string with the subarray id",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Release(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes Release command on
        MCCS controller device

        :return: a tuple containing Resultcode and Message
        :rtype: Tuple
        """

        command_id = f"{time.time()}-Release"
        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault("Release", command_id)

        if self._raise_exception:
            self.logger.info("exception thread")
            thread = threading.Thread(
                target=self.wait_and_update_exception, args=[command_id]
            )
            thread.start()
            return [ResultCode.QUEUED], [command_id]

        argin_json = json.loads(argin)
        subarray_id = int(argin_json["subarray_id"])
        mccs_subarray_device_name = "low-mccs/subarray/" + f"{subarray_id:02}"
        dev_factory = DevFactory()
        mccs_subarray_proxy = dev_factory.get_device(mccs_subarray_device_name)
        mccs_subarray_proxy.ReleaseResources(argin)
        thread = threading.Thread(
            target=self.update_lrcr, args=["Release", command_id]
        )
        thread.start()
        self.logger.info("Release command invoked on MCCS Controller")
        return [ResultCode.QUEUED], [command_id]

    def is_RestartSubarray_allowed(self) -> bool:
        """
        This method checks if the RestartSubarray command is allowed in the
        current device state.
        :return: ``True`` if the command is allowed
        :rtype:bool
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("RestartSubarray Command is allowed")
        return True

    @command(
        dtype_in=int,
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def RestartSubarray(
        self, argin: int
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This is the method to invoke RestartSubarray command.
        :param argin: an integer subarray_id.
        :return: ResultCode, command id
        :rtype: tuple
        """
        command_id = f"{time.time()}-RestartSubarray"
        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault("RestartSubarray", command_id)

        if self._raise_exception:
            self.logger.info("exception thread")
            thread = threading.Thread(
                target=self.wait_and_update_exception, args=[command_id]
            )
            thread.start()
            return [ResultCode.QUEUED], [command_id]

        mccs_subarray_device_name = "low-mccs/subarray/" + f"{argin:02}"
        dev_factory = DevFactory()
        mccs_subarray_proxy = dev_factory.get_device(mccs_subarray_device_name)
        mccs_subarray_proxy.Restart()

        thread = threading.Thread(
            target=self.update_lrcr, args=["RestartSubarray", command_id]
        )
        thread.start()
        self.logger.info("RestartSubarray command invoked on MCCS Controller")
        return [ResultCode.QUEUED], [command_id]

    # pylint: disable=arguments-renamed
    def push_command_result(
        self, result: ResultCode, command_id: str, exception: str = ""
    ) -> None:
        """Push long running command result event for given command.

        :params:

        result: The result code to be pushed as an event
        dtype: ResultCode

        command_id: The command_id for which the event is being pushed
        dtype: str

        exception: Exception message to be pushed as an event
        dtype: str
        """

        if exception:
            command_result = (
                command_id,
                json.dumps([ResultCode.FAILED, exception]),
            )
            self.push_change_event("longRunningCommandResult", command_result)
        command_result = (command_id, json.dumps([result, ""]))

        self.push_change_event("longRunningCommandResult", command_result)
        self.logger.info(
            "command_result has been pushed as %s", command_result
        )
