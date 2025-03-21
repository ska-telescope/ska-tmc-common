"""
A common module for different helper devices(mock devices)"
"""

import json
import threading
import time
from typing import List, Tuple

import tango
from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import AdminMode, HealthState, ObsState
from tango import DevState
from tango.server import AttrWriteType, attribute, command, run

from ska_tmc_common import CommandNotAllowed, FaultType
from ska_tmc_common.admin_mode_decorator import admin_mode_check
from ska_tmc_common.enum import PointingState
from ska_tmc_common.test_helpers.constants import SETADMINMODE
from ska_tmc_common.test_helpers.empty_component_manager import (
    EmptyComponentManager,
)


# pylint: disable=attribute-defined-outside-init,invalid-name
class HelperBaseDevice(SKABaseDevice):
    """A common base device for helper devices."""

    def init_device(self) -> None:
        super().init_device()
        self._delay: int = 2
        self._health_state = HealthState.OK
        self.dev_name = self.get_name()
        self._isSubsystemAvailable = True
        self._admin_mode: AdminMode = AdminMode.ONLINE
        self._isAdminModeEnabled: bool = True
        self.defective_params = {
            "enabled": False,
            "fault_type": FaultType.FAILED_RESULT,
            "error_message": "Default exception.",
            "result": ResultCode.FAILED,
        }

    class InitCommand(SKABaseDevice.InitCommand):
        """A class for the HelperBaseDevice's init_device() command."""

        def do(self) -> Tuple[ResultCode, str]:
            super().do()
            self._device.set_change_event("isSubsystemAvailable", True, False)
            self._device.set_change_event("adminMode", True, False)
            return (ResultCode.OK, "")

    def create_component_manager(self) -> EmptyComponentManager:
        """
        Creates an instance of EmptyComponentManager
        :return: component manager instance
        :rtype: EmptyComponentManager
        """
        empty_component_manager = EmptyComponentManager(
            logger=self.logger,
            communication_state_callback=None,
            component_state_callback=None,
        )
        return empty_component_manager

    delay = attribute(dtype=int, access=AttrWriteType.READ)
    defective = attribute(dtype=str, access=AttrWriteType.READ)
    isSubsystemAvailable = attribute(dtype=bool, access=AttrWriteType.READ)
    isAdminModeEnabled = attribute(dtype=bool, access=AttrWriteType.READ_WRITE)
    adminMode = attribute(
        dtype=AdminMode,
        access=AttrWriteType.READ_WRITE,
        label="Admin Mode",
        doc="Admin mode of the device.",
    )

    def read_isAdminModeEnabled(self) -> bool:
        """
        This method is used to read the attribute value for isAdminModeEnabled.
        :return: isAdminModeEnabled
        """
        return self._isAdminModeEnabled

    def write_isAdminModeEnabled(self, value: bool):
        """
        This method is used to write the attribute value for isAdminModeEnabled
        :param value: The new value to set for isAdminModeEnabled.
        """
        self._isAdminModeEnabled = value

    def read_delay(self) -> int:
        """
        This method is used to read the attribute value for delay.
        :return: delay
        """
        return self._delay

    def read_defective(self) -> str:
        """
        Returns defective status of devices
        :return: attribute value for defective params
        :rtype: str
        """
        return json.dumps(self.defective_params)

    def read_isSubsystemAvailable(self) -> bool:
        """
        Returns availability status for the leaf nodes devices
        :return: availabitlity status
        :rtype: bool
        """
        return self._isSubsystemAvailable

    def read_adminMode(self) -> AdminMode:
        """
        This method reads the adminMode value of the device.
        :return: admin_mode value
        :rtype: AdminMode
        """
        return self._admin_mode

    def write_adminMode(self, value):
        """
        This method writes the adminMode value of the device.
        """
        if self._admin_mode != value:
            self._admin_mode = value
            self.logger.info("AdminMode set to %s", self._admin_mode)
            self.push_change_event("adminMode", self._admin_mode)

    def always_executed_hook(self) -> None:
        pass

    def delete_device(self) -> None:
        pass

    @command(
        dtype_in=int,
        doc_in="Set Delay",
    )
    def SetDelay(self, delay: int) -> None:
        """
        Set the delay value.
        :param delay: Delay to be set
        :type delay: int
        """
        self._delay = delay

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

    def induce_fault(
        self, command_name: str, command_id: str, is_dish: bool = False
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        Induces a fault into the device based on the given parameters.

        :param command_name: The name of the command for which a fault is
            being induced.
        :type command_name: str
        :param command_id: The command id over which the LRCR event is to be
            pushed.
        :type command_id: str

        :return: ResultCode and Unique_ID
        :rtype: Tuple[List[ResultCode], List[str]]

        Example:
            defective_params = json.dumps({"enabled": False,"fault_type":
            FaultType.FAILED_RESULT,"error_message": "Default exception.",
            "result": ResultCode.FAILED,})
            proxy.SetDefective(defective_params)

        Explanation:
        This method induces various types of faults into a device to test its
        robustness and error-handling capabilities.

        - FAILED_RESULT:
            A fault type that triggers a failed result code
            for the command. The device will return a result code of 'FAILED'
            along with a unique_id indicating that the command execution has
            failed.

        - LONG_RUNNING_EXCEPTION:
            A fault type where a failed result will be sent over the
            LongRunningCommandResult attribute in 'delay' amount of time.

        - STUCK_IN_INTERMEDIATE_STATE:
            This fault type makes it such that the device is stuck in the given
            Observation state.

        - COMMAND_NOT_ALLOWED_AFTER_QUEUING:
            This fault type sends a ResultCode.NOT_ALLOWED event through the
            LongRunningCommandResult attribute.

        - COMMAND_NOT_ALLOWED_EXCEPTION_AFTER_QUEUING:
            This fault type sends a ResultCode.REJECTED event through the
            LongRunningCommandResult attribute.

        """
        fault_type = self.defective_params.get("fault_type")
        result = self.defective_params.get("result", ResultCode.FAILED)
        fault_message = self.defective_params.get(
            "error_message", "Exception occurred"
        )

        if not is_dish:
            intermediate_state = (
                self.defective_params.get("intermediate_state")
                or ObsState.RESOURCING
            )
        else:
            intermediate_state = (
                self.defective_params.get("intermediate_state")
                or PointingState.READY
            )

        if fault_type == FaultType.FAILED_RESULT:
            return [result], [fault_message]

        if fault_type == FaultType.LONG_RUNNING_EXCEPTION:
            thread = threading.Timer(
                self._delay,
                function=self.push_command_result,
                args=[result, command_name],
                kwargs={"message": fault_message, "command_id": command_id},
            )
            thread.start()
            return [ResultCode.QUEUED], [command_id]

        if fault_type == FaultType.STUCK_IN_INTERMEDIATE_STATE:
            self._obs_state = intermediate_state
            if not is_dish:
                self.push_obs_state_event(intermediate_state)
            else:
                self.push_pointing_state_event(intermediate_state)
            return [ResultCode.QUEUED], [command_id]

        if fault_type == FaultType.COMMAND_NOT_ALLOWED_AFTER_QUEUING:
            thread = threading.Timer(
                self._delay,
                function=self.push_command_result,
                args=[
                    ResultCode.NOT_ALLOWED,
                    command_name,
                ],
                kwargs={
                    "message": "Command is not allowed",
                    "command_id": command_id,
                },
            )
            thread.start()
            return [ResultCode.QUEUED], [command_id]

        if fault_type == FaultType.COMMAND_NOT_ALLOWED_EXCEPTION_AFTER_QUEUING:
            thread = threading.Timer(
                self._delay,
                function=self.push_command_result,
                args=[
                    ResultCode.REJECTED,
                    command_name,
                ],
                kwargs={
                    "message": (
                        "Exception from 'is_cmd_allowed' method: "
                        + f"{fault_message}"
                    ),
                    "command_id": command_id,
                },
            )
            thread.start()
            return [ResultCode.QUEUED], [command_id]

        if fault_type in [
            FaultType.GPM_JSON_ERROR,
            FaultType.GPM_URI_ERROR,
            FaultType.GPM_URI_NOT_REACHABLE,
            FaultType.GPM_ERROR_REPORTED_BY_DISH,
        ]:
            thread = threading.Timer(
                self._delay,
                function=self.push_command_result,
                args=[result, command_name],
                kwargs={"message": fault_message, "command_id": command_id},
            )
            thread.start()
            return [ResultCode.QUEUED], [command_id]

        return [ResultCode.OK], [command_id]

    def push_pointing_state_event(self, pointing_state: PointingState) -> None:
        """Push Pointing State Change Event"""
        with tango.EnsureOmniThread():
            self.logger.info(
                "Pushing change event for %s: %s",
                self.dev_name,
                pointing_state,
            )
            self._pointing_state = pointing_state
            self.push_change_event("pointingState", self._pointing_state)

    def push_command_result(
        self,
        result_code: ResultCode,
        command_name: str,
        message: str = "Command Completed",
        command_id: str = "",
    ) -> None:
        """
        Push long running command result event for given command.

        :param result_code: The result code to be pushed as an event
        :type result_code: ResultCode
        :param command_name: The command name for which event is being pushed
        :type command_name: str
        :param message: The message associated with the command result
        :type message: str
        :param command_id: The unique command id
        :type command_id: str
        """

        if not command_id:
            command_id = f"{time.time()}-{command_name}"
        command_result = (
            command_id,
            json.dumps((result_code, message)),
        )
        self.logger.info(
            "Pushing longRunningCommandResult Event with data: %s",
            command_result,
        )
        self.push_change_event("longRunningCommandResult", command_result)

    @command(
        dtype_in="DevState",
        doc_in="state to assign",
    )
    def SetDirectState(self, argin: tango.DevState) -> None:
        """
        Trigger a DevState change

        :param tango.DevState
        """
        # import debugpy; debugpy.debug_this_thread()
        if self.dev_state() != argin:
            self.set_state(argin)
            self.push_change_event("State", self.dev_state())
            self.logger.info("Device state is set to %s", self.dev_state())

    @command(
        dtype_in=bool,
        doc_in="Set Availability of the device",
    )
    def SetSubsystemAvailable(self, value: bool) -> None:
        """
        Sets Availability of the device
        :rtype: bool
        """
        self.logger.info("Setting the avalability value to : %s", value)
        if self._isSubsystemAvailable != value:
            self._isSubsystemAvailable = value
            self.push_change_event(
                "isSubsystemAvailable", self._isSubsystemAvailable
            )

    @command(
        dtype_in=int,
        doc_in="state to assign",
    )
    def SetDirectHealthState(self, argin: HealthState) -> None:
        """
        Trigger a HealthState change
        :param tango.DevState
        """
        # import debugpy; debugpy.debug_this_thread()
        self.logger.info(
            "HealthState value for simulator is : %s", self._health_state
        )
        value = HealthState(argin)
        if self._health_state != value:
            self._health_state = HealthState(argin)
            self.push_change_event("healthState", self._health_state)
            self.logger.info(
                "HealthState is set to: %s", self._health_state.name
            )

    @admin_mode_check()
    def is_On_allowed(self) -> bool:
        """
        This method checks if the On command is allowed in current state.
        :rtype: bool
        :return: ``True`` if the command is allowed
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
        self.logger.info("On command is allowed")
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def On(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes On command
        :return: ResultCode and message
        :rtype: Tuple
        """
        command_id = f"{time.time()}_On"
        self.logger.info("Instructed simulator to invoke On command")

        if self.defective_params["enabled"]:
            return self.induce_fault(
                "On",
                command_id,
            )
        if self.dev_state() != DevState.ON:
            self.set_state(DevState.ON)
            self.push_change_event("State", self.dev_state())
            self.logger.info("On command completed.")
        return [ResultCode.QUEUED], [command_id]

    @admin_mode_check()
    def is_Off_allowed(self) -> bool:
        """
        This method checks if the Off command is allowed in current state.
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
        self.logger.info("Off command is allowed")
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Off(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes Off command
        :return: ResultCode and message
        :rtype: Tuple
        """
        command_id = f"{time.time()}_Off"
        self.logger.info("Instructed simulator to invoke Off command")

        if self.defective_params["enabled"]:
            return self.induce_fault(
                "Off",
                command_id,
            )
        if self.dev_state() != DevState.OFF:
            self.set_state(DevState.OFF)
            self.push_change_event("State", self.dev_state())
            self.logger.info("Off command completed.")
        return [ResultCode.QUEUED], [command_id]

    @admin_mode_check()
    def is_Standby_allowed(self) -> bool:
        """
        This method checks if the Standby command is allowed in current state.
        :return: ``True`` if the command is allowed
        :rtype: bool
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
            ):
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("Standby command is allowed")
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Standby(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes Standby command
        :return: ResultCode and message
        :rtype: Tuple
        """
        command_id = f"{time.time()}_Standby"
        self.logger.info("Instructed simulator to invoke Standby command")

        if self.defective_params["enabled"]:
            return self.induce_fault(
                "Standby",
                command_id,
            )
        if self.dev_state() != DevState.STANDBY:
            self.set_state(DevState.STANDBY)
            self.push_change_event("State", self.dev_state())
            self.logger.info("Standy command completed.")
        return [ResultCode.QUEUED], [command_id]

    def is_SetAdminMode_allowed(self) -> bool:
        """
        This method checks if SetAdminMode command is allowed in the current
        device state.
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
        self.logger.info("SetAdminMode Command is allowed")
        return True

    @command(
        dtype_in="DevEnum",
        doc_in="The input string in JSON format.",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetAdminMode(self, argin) -> Tuple[List[ResultCode], List[str]]:
        """
        This is the method to invoke SetAdminMode command.
        :return: ResultCode, message
        :rtype: tuple
        """
        value = AdminMode(argin)
        self.logger.debug("The input adminmode is %s", value)
        command_id = f"{time.time()}_SetAdminMode"
        self.update_command_info(SETADMINMODE, str(value))
        if self.defective_params["enabled"]:
            return self.induce_fault("SetAdminMode", command_id)
        self.logger.info("The adminmode is %s", self._admin_mode)
        self.push_change_event("adminMode", self._admin_mode)
        self.logger.debug("SetAdminMode invoke on leafnode")
        return [ResultCode.QUEUED], [command_id]

    @admin_mode_check()
    def is_Disable_allowed(self) -> bool:
        """
        This method checks if the Disable command is allowed in current state.
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
        self.logger.info("Disable command is allowed")
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Disable(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes Disable command
        :return: ResultCode and message
        :rtype: Tuple
        """
        command_id = f"{time.time()}_Disable"
        if self.defective_params["enabled"]:
            return self.induce_fault(
                "Disable",
                command_id,
            )
        if self.dev_state() != DevState.DISABLE:
            self.set_state(DevState.DISABLE)
            self.push_change_event("State", self.dev_state())
            self.logger.info("Disable command completed.")
        return [ResultCode.OK], [command_id]


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """
    Runs the HelperBaseDevice Tango device.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: integer. Exit code of the run method.
    """
    return run((HelperBaseDevice,), args=args, **kwargs)


if __name__ == "__main__":
    main()
