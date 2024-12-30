"""
This module implements the Helper MCCS master leaf node devices for testing
an integrated TMC
"""

import threading
import time
from typing import List, Tuple

from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from tango.server import command

from ska_tmc_common import CommandNotAllowed, FaultType
from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice


# pylint: disable=attribute-defined-outside-init,invalid-name
class HelperMCCSMasterLeafNode(HelperBaseDevice):
    """A helper MCCS master leafnode device for triggering state
    changes with a command"""

    def init_device(self) -> None:
        super().init_device()
        self._isSubsystemAvailable = True

    class InitCommand(SKABaseDevice.InitCommand):
        """A class for the HelperMccsStateDevice's init_device() "command"."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            :return: ResultCode, message
            :rtype:tuple
            """
            super().do()
            self._device.set_change_event("isSubsystemAvailable", True, False)
            self._device.op_state_model.perform_action("component_on")
            return (ResultCode.OK, "")

    def is_AssignResources_allowed(self) -> bool:
        """
        Check if command `AssignResources` is allowed in the current device
        state.

        :return: ``True`` if the command is allowed
        :rtype: bool
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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

        # AdminMode check
        proceed, result, message = self._check_admin_mode("AssignResources")
        if not proceed:
            return result, message

        if self.defective_params["enabled"]:
            return self.induce_fault("AssignResources", command_id)

        thread = threading.Timer(
            self._delay,
            self.push_command_result,
            args=[ResultCode.OK, "AssignResources"],
            kwargs={"command_id": command_id},
        )
        thread.start()

        self.logger.info(
            "AssignResourses command complete with argin: %s", argin
        )
        return [ResultCode.QUEUED], [command_id]

    def is_ReleaseAllResources_allowed(self) -> bool:
        """
        Check if command `ReleaseAllResources` is allowed in the current
        device state.

        :return: ``True`` if the command is allowed
        :raises CommandNotAllowed: command is not allowed
        :rtype: bool
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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
        command_id = f"{time.time()}-ReleaseAllResources"
        if self.defective_params["enabled"]:
            return self.induce_fault("ReleaseAllResources", command_id)
        thread = threading.Timer(
            self._delay,
            self.push_command_result,
            args=[ResultCode.OK, "ReleaseAllResources"],
            kwargs={"command_id": command_id},
        )
        thread.start()
        self.logger.info(
            "ReleaseAllResources command complete with argin: %s", argin
        )
        return [ResultCode.QUEUED], [command_id]
