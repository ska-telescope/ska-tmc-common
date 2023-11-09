# pylint: disable=C0302
"""
This module implements the Helper Dish Leaf Node Device for testing an
integrated TMC.
"""
import json
import threading
import time
from typing import List, Tuple

from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from tango import AttrWriteType, DevState
from tango.server import attribute, command, run

from ska_tmc_common import CommandNotAllowed, FaultType
from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice

from .constants import (
    ABORT,
    ABORT_COMMANDS,
    CONFIGURE,
    OFF,
    RESTART,
    SCAN,
    SET_OPERATE_MODE,
    SET_STANDBY_FP_MODE,
    SET_STANDBY_LP_MODE,
    SET_STOW_MODE,
    TRACK,
    TRACK_STOP,
)


# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument,too-many-public-methods
class HelperDishLNDevice(HelperBaseDevice):
    """A device exposing commands and attributes of the Dish Leaf Node
    device.
    """

    def init_device(self) -> None:
        super().init_device()
        self._delay: int = 2
        self._command_delay_info: dict = {
            CONFIGURE: 2,
            ABORT: 2,
            RESTART: 2,
        }
        self._command_call_info: list = []
        self._command_info: Tuple = ("", "")
        self._state_duration_info: list = []
        self._offset: dict = {"off_xel": 0.0, "off_el": 0.0}
        self._actual_pointing: list = []
        self._kvalue: int = 0
        self._isSubsystemAvailable = False

    class InitCommand(SKABaseDevice.InitCommand):
        """A class for the HelperDishLNDevice's init_device() command."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            """
            super().do()
            self._device.set_change_event("commandCallInfo", True, False)
            self._device.set_change_event("isSubsystemAvailable", True, False)
            self._device.set_change_event("actualPointing", True, False)
            return (ResultCode.OK, "")

    defective = attribute(dtype=str, access=AttrWriteType.READ)
    delay = attribute(dtype=int, access=AttrWriteType.READ)
    actualPointing = attribute(dtype=str, access=AttrWriteType.READ)
    kValue = attribute(dtype=int, access=AttrWriteType.READ)
    isSubsystemAvailable = attribute(dtype=bool, access=AttrWriteType.READ)

    def read_kValue(self) -> int:
        """
        This method reads the k value of the dish.
        :rtype:int
        """
        return self._kvalue

    def read_delay(self) -> int:
        """This method is used to read the attribute value for delay."""
        return self._delay

    def read_defective(self) -> str:
        """
        Returns defective status of devices

        :rtype: str
        """
        return self._defective

    def read_actualPointing(self) -> str:
        """Read method for actual pointing."""
        return json.dumps(self._actual_pointing)

    def read_isSubsystemAvailable(self) -> bool:
        """
        Returns avalability status for the leaf nodes devices

        :rtype: bool
        """
        return self._isSubsystemAvailable

    commandDelayInfo = attribute(dtype=str, access=AttrWriteType.READ)

    commandCallInfo = attribute(
        dtype=(("str",),),
        access=AttrWriteType.READ,
        max_dim_x=100,
        max_dim_y=100,
    )

    def set_offset(self, cross_elevation: float, elevation: float) -> None:
        """Sets the offset for Dish."""
        self._offset["off_xel"] = cross_elevation
        self._offset["off_el"] = elevation

    def read_commandCallInfo(self):
        """This method is used to read the attribute value for
        commandCallInfo.
        """
        return self._command_call_info

    def read_commandDelayInfo(self) -> str:
        """This method is used to read the attribute value for delay."""
        return json.dumps(self._command_delay_info)

    def is_SetKValue_allowed(self) -> bool:
        """
        This method checks if the SetKValue Command is allowed in current
        State.
        :rtype: bool
        """
        return True

    @command(
        dtype_in="DevLong",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetKValue(self, kvalue: int) -> Tuple[List[ResultCode], List[str]]:
        """
        This command invokes SetKValue command on  Dish Master.

        :param argin: k value between range 1-2222.
        :argin dtype: int
        :rtype: Tuple[List[ResultCode], List[str]]
        """
        if self.defective_params["enabled"]:
            return [ResultCode.FAILED], [
                self.defective_params["error_message"]
            ]
        self._kvalue = kvalue
        return ([ResultCode.OK], [""])

    @command(
        dtype_in=str,
        doc_in="Set Delay",
    )
    def SetDelay(self, command_delay_info: str) -> None:
        """Update delay value"""
        self.logger.info(
            "Setting the Delay value for Dish simulator to : %s",
            command_delay_info,
        )
        # set command info
        command_delay_info_dict = json.loads(command_delay_info)
        for key, value in command_delay_info_dict.items():
            self._command_delay_info[key] = value
        self.logger.info("Command Delay Info Set %s", self._command_delay_info)

    @command(
        doc_in="Reset Delay",
    )
    def ResetDelay(self) -> None:
        """Reset Delay to it's default values"""
        self.logger.info("Resetting Command Delays for Dish Master Simulator")
        # Reset command info
        self._command_delay_info = {
            CONFIGURE: 2,
            ABORT: 2,
            RESTART: 2,
        }

    @command(
        doc_in="Clears commandCallInfo",
    )
    def ClearCommandCallInfo(self) -> None:
        """Clears commandCallInfo to empty list"""
        self.logger.info("Clearing CommandCallInfo for DishMaster simulators")
        self._command_call_info.clear()
        self.push_change_event("commandCallInfo", self._command_call_info)

    def push_command_result(
        self, result: ResultCode, command: str, exception: str = ""
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
        if result == ResultCode.OK:
            self.logger.info("Successfully processed %s command", command)
        else:
            self.logger.info(
                "Command %s failed, ResultCode: %d", command, result
            )
        command_id = f"{time.time()}-{command}"
        if exception:
            command_result = (command_id, exception)
            self.push_change_event("longRunningCommandResult", command_result)
        command_result = (command_id, json.dumps(result))
        self.push_change_event("longRunningCommandResult", command_result)

    def is_Off_allowed(self) -> bool:
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("Off Command is allowed")
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Off(self):
        self.logger.info("Instructed Dish simulator to invoke Off command")
        self.update_command_info(OFF, "")
        if self.defective_params["enabled"]:
            return self.induce_fault(
                "Off",
            )
        if self.dev_state() != DevState.OFF:
            self.set_state(DevState.OFF)
            self.push_change_event("State", self.dev_state())
        self.push_command_result(ResultCode.OK, "Off")
        self.logger.info("Off command completed.")
        return [ResultCode.OK], [""]

    def is_SetStandbyFPMode_allowed(self) -> bool:
        """
        This method checks if the is_SetStandbyFPMode_allowed Command is
        allowed in current
        State.
        :rtype:bool
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
        self.logger.info("SetStandbyFPMode Command is allowed")
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetStandbyFPMode(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes SetStandbyFPMode command on  Dish Master
        :rtype: tuple
        """
        self.logger.info("Processing SetStandbyFPMode Command")
        self.update_command_info(SET_STANDBY_FP_MODE, "")
        if self.defective_params["enabled"]:
            return self.induce_fault("SetStandbyFPMode")
        if self.dev_state() != DevState.STANDBY:
            self.set_state(DevState.STANDBY)
            time.sleep(0.1)
            self.push_change_event("State", self.dev_state())

        self.push_command_result(ResultCode.OK, "SetStandbyFPMode")
        self.logger.info("SetStandbyFPMode command completed.")
        return ([ResultCode.OK], [""])

    def is_SetStandbyLPMode_allowed(self) -> bool:
        """
        This method checks if the is_SetStandbyLPMode_allowed Command is
        allowed in current
        State.
        :rtype: bool
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
        self.logger.info("SetStandbyLPMode Command is allowed")
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetStandbyLPMode(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes SetStandbyLPMode command on  Dish Master
        :rtype: tuple
        """
        self.logger.info(
            "Instructed Dish simulator to invoke SetStandbyLPMode command"
        )
        self.update_command_info(SET_STANDBY_LP_MODE, "")
        if self.defective_params["enabled"]:
            return self.induce_fault("SetStandbyLPMode")
        # Set the device state
        if self.dev_state() != DevState.STANDBY:
            self.set_state(DevState.STANDBY)
            time.sleep(0.1)
            self.push_change_event("State", self.dev_state())

        self.push_command_result(ResultCode.OK, "SetStandbyLPMode")
        self.logger.info("SetStandbyLPMode command completed.")
        return ([ResultCode.OK], [""])

    def is_SetOperateMode_allowed(self) -> bool:
        """
        This method checks if the SetOperateMode Command is allowed in current
        State.
        :rtype:bool
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
        self.logger.info("SetOperateMode Command is allowed")
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetOperateMode(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes SetOperateMode command on  Dish Master
        :rtype: tuple
        """
        self.logger.info(
            "Instructed Dish simulator to invoke SetOperateMode command"
        )
        self.update_command_info(SET_OPERATE_MODE, "")
        if self.defective_params["enabled"]:
            return self.induce_fault("SetOperateMode")

        # Set the device state
        if self.dev_state() != DevState.ON:
            self.set_state(DevState.ON)
            time.sleep(0.1)
            self.push_change_event("State", self.dev_state())

        self.push_command_result(ResultCode.OK, "SetOperateMode")
        self.logger.info("SetOperateMode command completed.")
        return ([ResultCode.OK], [""])

    def is_SetStowMode_allowed(self) -> bool:
        """
        This method checks if the SetStowMode Command is allowed in current
        State.
        :rtype: bool
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
        self.logger.info("SetStowMode Command is allowed")
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetStowMode(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes SetStowMode command on  Dish Master
        :rtype : tuple
        """
        self.logger.info(
            "Instructed Dish simulator to invoke SetStowMode command"
        )
        self.update_command_info(SET_STOW_MODE, "")
        if self.defective_params["enabled"]:
            return self.induce_fault("SetStowMode")

        # Set device state
        if self.dev_state() != DevState.DISABLE:
            self.set_state(DevState.DISABLE)
            time.sleep(0.1)
            self.push_change_event("State", self.dev_state())

        self.push_command_result(ResultCode.OK, "SetStowMode")
        self.logger.info("SetStowMode command completed.")
        return ([ResultCode.OK], [""])

    def is_Track_allowed(self) -> bool:
        """
        This method checks if the Track Command is allowed in current
        State.
        :rtype: bool
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
        self.logger.info(" Track Command is allowed")
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Track(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes Track command on  Dish Master
        :rtype: tuple
        """
        self.logger.info("Instructed Dish simulator to invoke Track command")
        self.update_command_info(TRACK, "")
        if self.defective_params["enabled"]:
            return self.induce_fault("Track")

        self.push_command_result(ResultCode.OK, "Track")
        self.logger.info("Track command completed.")
        return ([ResultCode.OK], [""])

    def is_TrackStop_allowed(self) -> bool:
        """
        This method checks if the TrackStop Command is allowed in current
        State.
        :rtype: bool
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
        self.logger.info("TrackStop Command is allowed")
        return True

    @command(
        dtype_in="DevVoid",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def TrackStop(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes TrackStop command on  Dish Master
        """
        self.logger.info(
            "Instructed Dish simulator to invoke TrackStop command"
        )
        self.update_command_info(TRACK_STOP, "")
        if self.defective_params["enabled"]:
            return self.induce_fault("TrackStop")

        self.push_command_result(ResultCode.OK, "TrackStop")
        self.logger.info("TrackStop command completed.")
        return ([ResultCode.OK], [""])

    def is_AbortCommands_allowed(self) -> bool:
        """
        This method checks if the AbortCommands command is allowed in current
        State.
        :rtype: bool
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
        self.logger.info("AbortCommands Command is allowed")
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def AbortCommands(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes AbortCommands command on  Dish Master
        :rtype: tuple
        """
        self.logger.info(
            "Instructed Dish simulator to invoke AbortCommands command"
        )
        self.update_command_info(ABORT_COMMANDS, "")

        if self.defective_params["enabled"]:
            return self.induce_fault("AbortCommands")

        self.logger.info("Abort Completed")
        return ([ResultCode.OK], [""])

    def is_Configure_allowed(self) -> bool:
        """
        This method checks if the Configure Command is allowed in current
        State.
        :rtype: bool
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
        self.logger.info("Configure Command is allowed")
        return True

    @command(
        dtype_in=("DevString"),
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Configure(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes Configure command on  Dish Master
        :rtype: tuple
        """
        command_id = f"{time.time()}_Configure"
        self.logger.info("Processing Configure command")
        # to record the command data
        self.logger.info(
            "Instructed Dish simulator to invoke Configure command"
        )
        self.update_command_info(CONFIGURE, argin)
        if self.defective_params["enabled"]:
            return self.induce_fault("Configure")

        thread = threading.Timer(
            self._delay,
            self.push_change_event,
            args=["longRunningCommandResult", (command_id, ResultCode.OK)],
        )
        thread.start()
        self.logger.info("Configure command completed.")
        return [ResultCode.QUEUED], [command_id]

    def is_TrackLoadStaticOff_allowed(self) -> bool:
        """
        This method checks if the TrackLoadStaticOff command is allowed in
        current State.
        :rtype: bool
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
        self.logger.info("TrackLoadStaticOff Command is allowed")
        return True

    @command(
        dtype_in=("DevString"),
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def TrackLoadStaticOff(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes TrackLoadStaticOff command on  Dish Master.

        :param argin: A list containing scan_id/ time, cross elevation and
            elevation offsets.
        :argin dtype: str(List)
        :rtype: Tuple[List[ResultCode], List[str]]
        """
        self.logger.info(
            "Instructed Dish simulator to invoke TrackLoadStaticOff command"
        )

        if self.defective_params["enabled"]:
            return self.induce_fault("TrackLoadStaticOff")

        # Set offsets.
        input_offsets = json.loads(argin)
        cross_elevation = input_offsets[0]
        elevation = input_offsets[1]
        self.set_offset(cross_elevation, elevation)
        self.push_command_result(ResultCode.OK, "TrackLoadStaticOff")
        self.logger.info("TrackLoadStaticOff command completed.")
        return ([ResultCode.OK], [""])

    def update_command_info(
        self, command_name: str = "", command_input: str = ""
    ) -> None:
        """This method updates the commandCallInfo attribute,
        with the respective command information.

        Args:
            command_name (str): command name
            command_input (str): Input argin for command
        """
        self.logger.info(
            "Recording the command data for DishMaster simulators"
        )

        self._command_info = (command_name, command_input)
        self._command_call_info.append(self._command_info)
        self.logger.info(
            "Recorded command_call_info list for DishMaster simulators \
            is %s",
            self._command_call_info,
        )
        self.push_change_event("commandCallInfo", self._command_call_info)
        self.logger.info("CommandCallInfo updates are pushed")

    # TODO: Enable the commands when they are implemented in Dish Leaf Node.
    # def is_Slew_allowed(self) -> bool:
    #     """
    #     This method checks if the Slew command is allowed in current State.
    #     :rtype:bool
    #     """
    #     if self.defective_params["enabled"]:
    #         if (
    #             self.defective_params["fault_type"]
    #             == FaultType.COMMAND_NOT_ALLOWED
    #         ):
    #             self.logger.info(
    #                 "Device is defective, cannot process command."
    #             )
    #             raise CommandNotAllowed(
    #               self.defective_params["error_message"]
    #             )
    #     self.logger.info("Slew Command is allowed")
    #     return True

    # @command(
    #     dtype_in=("DevVoid"),
    #     dtype_out="DevVarLongStringArray",
    #     doc_out="(ReturnType, 'informational message')",
    # )
    # def Slew(self) -> Tuple[List[ResultCode], List[str]]:
    #     """
    #     This method invokes Slew command on Dish Master
    #     """
    #     self.logger.info("Processing Slew Command")
    #     # to record the command data
    #     self.update_command_info(SLEW)
    #     if self.defective_params["enabled"]:
    #         return self.induce_fault("Slew")

    #     if self._pointing_state != PointingState.SLEW:
    #         self._pointing_state = PointingState.SLEW
    #         self.push_change_event("pointingState", self._pointing_state)
    #     self.logger.info("Slew command completed.")
    #     return ([ResultCode.OK], [""])

    # @command(
    #     dtype_in=("DevVoid"),
    #     dtype_out="DevVarLongStringArray",
    #     doc_out="(ReturnType, 'informational message')",
    # )
    # def StartCapture(self) -> Tuple[List[ResultCode], List[str]]:
    #     """
    #     This method invokes StartCapture command on Dish Master
    #     """
    #     # TBD: Dish mode changedoc_out="(ReturnType, 'DevVoid')",
    #     return ([ResultCode.OK], [""])

    # @command(
    #     dtype_in=("DevVoid"),
    #     dtype_out="DevVarLongStringArray",
    #     doc_out="(ReturnType, 'informational message')",
    # )
    # def SetMaintenanceMode(self) -> Tuple[List[ResultCode], List[str]]:
    #     """
    #     This method sets the Maintainance Mode for the dish
    #     """
    #     # TBD: Dish mode change
    #     return ([ResultCode.OK], [""])

    def is_Scan_allowed(self) -> bool:
        """
        This method checks if the Scan Command is allowed in current State.
        :rtype:bool
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
        self.logger.info("Scan Command is allowed")
        return True

    @command(
        dtype_in=("DevVoid"),
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Scan(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes Scan command on Dish Master
        """
        self.logger.info("Processing Scan Command")
        # to record the command data
        self.update_command_info(SCAN)
        if self.defective_params["enabled"]:
            return self.induce_fault("Scan")

            # TBD: Add your dish mode change logic here if required
        self.logger.info("Processing Scan")
        return ([ResultCode.OK], [""])

    # TODO: Enable below commands when Dish Leaf Node implements them.
    # def is_Reset_allowed(self) -> bool:
    #     """
    #     This method checks if the Reset command is allowed in current State.
    #     :rtype:bool
    #     """
    #     if self.defective_params["enabled"]:
    #         if (
    #             self.defective_params["fault_type"]
    #             == FaultType.COMMAND_NOT_ALLOWED
    #         ):
    #             self.logger.info(
    #                 "Device is defective, cannot process command."
    #             )
    #             raise CommandNotAllowed(
    #               self.defective_params["error_message"]
    #             )
    #     self.logger.info("Reset Command is allowed")
    #     return True

    # @command(
    #     dtype_out="DevVarLongStringArray",
    #     doc_out="(ReturnType, 'informational message')",
    # )
    # def Reset(self) -> Tuple[List[ResultCode], List[str]]:
    #     """
    #     This method invokes Reset command on Dish Master
    #     :rtype:tuple
    #     """
    #     self.logger.info("Processing Reset Command")
    #     # to record the command data
    #     self.update_command_info(RESET)
    #     if self.defective_params["enabled"]:
    #         return self.induce_fault("Reset")

    #         # TBD: Add your dish mode change logic here if required
    #     self.logger.info("Reset command completed.")
    #     return ([ResultCode.OK], [""])


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """
    Runs the HelperDishDevice Tango device.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: integer. Exit code of the run method.
    """
    return run((HelperDishLNDevice,), args=args, **kwargs)


if __name__ == "__main__":
    main()
