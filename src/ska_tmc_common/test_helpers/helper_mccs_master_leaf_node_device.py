"""
This module implements the Helper MCCS master leaf node devices for testing
an integrated TMC
"""
# pylint: disable=unused-argument
from typing import List, Tuple

from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from tango import AttrWriteType
from tango.server import attribute, command

from ska_tmc_common import CommandNotAllowed, FaultType
from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice


# pylint: disable=attribute-defined-outside-init
class HelperMCCSMasterLeafNode(HelperBaseDevice):
    """A generic device for triggering state changes with a command"""

    def init_device(self) -> None:
        super().init_device()
        self.dev_name = self.get_name()
        self._raise_exception = False

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

    assignedResources = attribute(dtype="DevString", access=AttrWriteType.READ)

    def read_assignedResources(self) -> str:
        """
        Reads the values of the assignedResources
        :rtype:str
        """
        return self._device._assigned_resources

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
        This method invokes AssignResources command on subarray device

        :return: a tuple containing ResultCode and Message
        :rtype: Tuple
        """
        self.logger.info("AssignResources command completed.")
        return [ResultCode.OK], [""]

    def is_ReleaseResources_allowed(self) -> bool:
        """
        Check if command `ReleaseResources` is allowed in the current
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
    def ReleaseResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes ReleaseResources command on subarray device

        :return: a tuple conataining Resultcose and Message
        :rtype: Tuple
        """
        self.logger.info("ReleaseResources command completed.")
        return [ResultCode.OK], [""]
