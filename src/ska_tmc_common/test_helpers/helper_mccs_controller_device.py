"""
This module implements the Helper MCCS controller devices for testing
an integrated TMC
"""
# pylint: disable=unused-argument
import json
from typing import List, Tuple

from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from tango.server import command

from ska_tmc_common import CommandNotAllowed, FaultType
from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice
import time
import threading

import tango

from .constants import (
    ABORT,
    ASSIGN_RESOURCES,
    CONFIGURE,
    END,
    RELEASE_ALL_RESOURCES,
    RELEASE_RESOURCES,
    RESTART,

)
# pylint: disable=attribute-defined-outside-init
class HelperMCCSController(HelperBaseDevice):
    """A helper MCCS controller device for triggering state changes
    with a command"""

    def init_device(self) -> None:
        super().init_device()
        self.dev_name = self.get_name()
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
        self._command_delay_info = {
            ASSIGN_RESOURCES: 2,
            CONFIGURE: 2,
            RELEASE_RESOURCES: 2,
            ABORT: 2,
            RESTART: 2,
            RELEASE_ALL_RESOURCES: 2,
            END: 2,
        }

    class InitCommand(SKABaseDevice.InitCommand):
        """A class for the HelperMCCSController's init_device() "command"."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            :returns: ResultCode, message
            :rtype:tuple
            """
            super().do()
            return (ResultCode.OK, "")

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
        for key, value in input_dict.items():
            self.defective_params[key] = value

    @command(
        dtype_in=bool,
        doc_in="Raise Exception",
    )
    def SetRaiseException(self, value: bool) -> None:
        """Set Raise Exception"""
        self.logger.info("Setting the raise exception value to : %s", value)
        self._raise_exception = value


    def push_command_result(
        self, command_id: str ,result: ResultCode, command: str, exception: str = ""
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
        #command_id = f"{time.time()}-{command}"
        if exception:
            command_result = (command_id, exception)
            self.push_change_event("longRunningCommandResult", command_result)
        command_result = (command_id, json.dumps(result))
        self.push_change_event("longRunningCommandResult", command_result)

    def update_lrcr(
        self ,command_name: str = "" , command_id : str = ""
    ) -> None:
        """Updates the given data after a delay."""
        # delay_value = 0
        # with tango.EnsureOmniThread():
        #     if command_name in self._command_delay_info:
        #         delay_value = self._command_delay_info[command_name]
        #     time.sleep(delay_value)
        #     self.logger.info(
        #         "Sleep %s for command %s ", delay_value, command_name
        #     )
        #
        #     time.sleep(0.1)
        self.push_command_result(command_id ,ResultCode.OK)
        self.logger.info("Command result pushed")
    def is_Allocate_allowed(self) -> bool:
        """
        Check if command `Allocate` is allowed in the current device
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
        self.logger.info("Allocate command started 1 ")
        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault(
                "Allocate",
            )
        self.logger.info("Allocate command started 2")
        if self._raise_exception:
            self.logger.info("exception")
            return [ResultCode.QUEUED], [""]


        command_id = f"1000_Allocate"

        thread = threading.Thread(
            target=self.update_lrcr,
            args = ["Allocate",command_id]


        )
        thread.start()
        self.logger.info(
            "AssignResourse invoked on MCCS Controller"
        )


        #return [ ResultCode.QUEUED, command_id ]
        return [ResultCode.QUEUED], [command_id]

    def is_Release_allowed(self) -> bool:
        """
        Check if command `Release` is allowed in the current
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
    def Release(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes Release command on
        MCCS controller device

        :return: a tuple containing Resultcode and Message
        :rtype: Tuple
        """
        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault(
                "Release",
            )

        if self._raise_exception:
            return [ResultCode.QUEUED], [""]
        self.logger.debug("Release command complete")
        return [ResultCode.OK], [""]
