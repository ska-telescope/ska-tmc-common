"""
This module implements the Helper MCCS master leaf node devices for testing
an integrated TMC
"""
# pylint: disable=unused-argument
import json
import time
from typing import List, Tuple

from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from tango.server import command

from ska_tmc_common import CommandNotAllowed, FaultType
from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice


# pylint: disable=attribute-defined-outside-init
class HelperMCCSMasterLeafNode(HelperBaseDevice):
    """A helper MCCS master leafnode device for triggering state
    changes with a command"""

    def init_device(self) -> None:
        super().init_device()
        self.dev_name = self.get_name()
        self._delay: int = 2
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

    class InitCommand(SKABaseDevice.InitCommand):
        """A class for the HelperMccsStateDevice's init_device() "command"."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            :returns: ResultCode, message
            :rtype:tuple
            """
            super().do()
            return (ResultCode.OK, "")

    def push_command_result(
        self, result: ResultCode, command_id: str, exception: str = ""
    ) -> None:
        """Push long running command result event for given command.

        :params:

        result: The result code to be pushed as an event
        dtype: ResultCode

        command: The command name for which the event is being pushed
        dtype: str

        exception: Exception message to be pushed as an event
        dtype: str
        """
        self.logger.debug("The values are:%s ,%s, %s",result,command_id,exception)
        self.logger.info("The values are:%s ,%s, %s",result,command_id,exception)
        if exception:
            command_result = (command_id, exception)
            self.logger.debug("Inside push_command_result exception.")
            self.logger.info("Inside push_command_result exception.")
            self.push_change_event("longRunningCommandResult", command_result)
        command_result = (command_id, json.dumps(result))
        self.logger.debug("Inside push_command_result")
        self.logger.info("Inside push_command_result")
        self.push_change_event("longRunningCommandResult", command_result)

    def is_AssignResources_allowed(self) -> bool:
        """
        Check if command `AssignResources` is allowed in the current device
        state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
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
        self.logger.info("AssignResources Command is allowed")
        return True

    @command(
        dtype_in="DevString",
        doc_in="JSON-encoded string with the resources to add to subarray",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def AssignResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes AssignResources command on MCCS
        master leaf node device.

        :return: a tuple containing ResultCode and Message
        :rtype: Tuple
        """
        command_id = f"{time.time()}-AssignResources"
        self.logger.debug("Inside AssignResources command.")
        self.logger.info("Inside AssignResources command.")
        if self.defective_params["enabled"]:
            self.logger.debug("AssignResourses is faulty on MCCSMLN.")
            self.logger.info("AssignResourses is faulty on MCCSMLN.")
            return self.induce_fault(
                "AssignResources",
            )
        self.logger.debug("AssignResourses command complete")
        self.logger.info("AssignResourses command complete")
        self.push_command_result(ResultCode.OK, command_id)
        self.logger.info("AssignResourses command complete")
        return [ResultCode.OK], [command_id]

    def is_ReleaseAllResources_allowed(self) -> bool:
        """
        Check if command `ReleaseAllResources` is allowed in the current
        device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
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
        doc_in="JSON-encoded string with the resources to remove from the \
            subarray",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ReleaseAllResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes ReleaseAllResources command on MCCS
        master leaf node device.

        :return: a tuple containing ResultCode and Message
        :rtype: Tuple
        """
        if self.defective_params["enabled"]:
            return self.induce_fault(
                "ReleaseAllResources",
            )
        self.push_command_result(ResultCode.OK, "ReleaseAllResources")
        self.logger.info("ReleaseAllResources command completed.")
        return [ResultCode.OK], [""]
