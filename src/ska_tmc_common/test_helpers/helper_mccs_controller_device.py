"""
This module implements the Helper MCCS controller devices for testing
an integrated TMC
"""

import json
import threading
import time
from typing import List, Tuple

from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import AdminMode
from tango import DevState
from tango.server import AttrWriteType, attribute, command, run

from ska_tmc_common import CommandNotAllowed, DevFactory, FaultType
from ska_tmc_common.admin_mode_decorator import admin_mode_check
from ska_tmc_common.test_helpers.constants import (
    ABORT,
    ALLOCATE,
    CONFIGURE,
    END,
    RELEASE,
    RESTART,
)
from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice


# pylint: disable=attribute-defined-outside-init,invalid-name
class HelperMCCSController(HelperBaseDevice):
    """A helper MCCS controller device for triggering state changes
    with a command"""

    def init_device(self) -> None:
        super().init_device()
        self.set_state(DevState.UNKNOWN)
        self._admin_mode: AdminMode = AdminMode.OFFLINE
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

    isAdminModeEnabled = attribute(dtype=bool, access=AttrWriteType.READ_WRITE)

    def read_isAdminModeEnabled(self):
        """
        Raise an AttributeError indicating 'isAdminModeEnabled' is unavailable.
        :raises AttributeError: Always raised to block access to the attribute.
        """
        raise AttributeError(
            "The 'isAdminModeEnabled' attribute is not available."
        )

    def write_isAdminModeEnabled(self, value: bool):
        """
        Raise an AttributeError indicating that 'isAdminModeEnabled'
        cannot be modified.
        :param value: The value attempted to set for isAdminModeEnabled.
        :raises AttributeError: Always raised to access to the attribute..
        """
        raise AttributeError(
            "The 'isAdminModeEnabled' attribute is not available."
        )

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

    @admin_mode_check()
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
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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

        argin_json = json.loads(argin)
        subarray_id = int(argin_json["subarray_id"])
        mccs_subarray_device_name = "low-mccs/subarray/" + f"{subarray_id:02}"
        dev_factory = DevFactory()
        mccs_subarray_proxy = dev_factory.get_device(mccs_subarray_device_name)
        mccs_subarray_proxy.AssignResources(argin)

        thread = threading.Timer(
            self._delay,
            self.push_command_result,
            args=[ResultCode.OK, "Allocate"],
            kwargs={
                "command_id": command_id,
            },
        )
        thread.start()
        self.logger.info("Allocate invoked on MCCS Controller")
        return [ResultCode.QUEUED], [command_id]

    @admin_mode_check()
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
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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

        argin_json = json.loads(argin)
        subarray_id = int(argin_json["subarray_id"])
        mccs_subarray_device_name = "low-mccs/subarray/" + f"{subarray_id:02}"
        dev_factory = DevFactory()
        mccs_subarray_proxy = dev_factory.get_device(mccs_subarray_device_name)
        mccs_subarray_proxy.ReleaseResources(argin)
        thread = threading.Thread(
            target=self.push_command_result,
            args=[ResultCode.OK, "Release"],
            kwargs={
                "command_id": command_id,
            },
        )
        thread.start()
        self.logger.info("Release command invoked on MCCS Controller")
        return [ResultCode.QUEUED], [command_id]

    @admin_mode_check()
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
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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

        mccs_subarray_device_name = "low-mccs/subarray/" + f"{argin:02}"
        dev_factory = DevFactory()
        mccs_subarray_proxy = dev_factory.get_device(mccs_subarray_device_name)
        mccs_subarray_proxy.Restart()

        thread = threading.Thread(
            target=self.push_command_result,
            args=[ResultCode.OK, "RestartSubarray"],
            kwargs={
                "command_id": command_id,
            },
        )
        thread.start()
        self.logger.info("RestartSubarray command invoked on MCCS Controller")
        return [ResultCode.QUEUED], [command_id]

    def induce_fault(
        self, command_name: str, command_id: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        Induces a fault into the device based on the given parameters.

        :param command_name: The name of the command for which a fault is
            being induced.
        :type command_name: str
        :param command_id: The command id over which the LRCR event is to be
            pushed.
        :type command_id: str

        Explanation:
        This method induces various types of faults into a device to test its
        robustness and error-handling capabilities.
        Overrided to fix time out issue on MCCS Master Leaf node.

        - STUCK_IN_INTERMEDIATE_STATE:
            This fault type makes it such that the device is stuck in the given
            Observation state.

        """

        fault_type = self.defective_params.get("fault_type")
        if fault_type == FaultType.STUCK_IN_INTERMEDIATE_STATE:
            return [ResultCode.QUEUED], [command_id]

        return super().induce_fault(command_name, command_id)


def main(args=None, **kwargs):
    """
    Runs the HelperMccsController Tango device.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: integer. Exit code of the run method.
    """
    return run((HelperMCCSController,), args=args, **kwargs)


if __name__ == "__main__":
    main()
