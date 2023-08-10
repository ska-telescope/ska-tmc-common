# pylint: disable=C0302
"""
This module implements the Helper Dish Device for testing an integrated TMC
"""
import json
import threading
import time
from typing import List, Tuple

import tango
from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from tango import AttrWriteType, DevEnum, DevState
from tango.server import attribute, command, run

from ska_tmc_common import CommandNotAllowed, FaultType
from ska_tmc_common.enum import DishMode, PointingState
from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice

from .constants import (
    ABORT,
    ABORT_COMMANDS,
    CONFIGURE,
    CONFIGURE_BAND_2,
    OFF,
    RESET,
    RESTART,
    SCAN,
    SET_OPERATE_MODE,
    SET_STANDBY_FP_MODE,
    SET_STANDBY_LP_MODE,
    SET_STOW_MODE,
    SLEW,
    STAND_BY,
    TRACK,
    TRACK_STOP,
)


# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument,too-many-public-methods
class HelperDishDevice(HelperBaseDevice):
    """A device exposing commands and attributes of the Dish device."""

    def init_device(self):
        super().init_device()
        self._delay = 2
        self._pointing_state = PointingState.NONE
        self._dish_mode = DishMode.STANDBY_LP
        self._command_delay_info = {
            CONFIGURE: 2,
            ABORT: 2,
            RESTART: 2,
        }
        self._command_call_info = []
        self._command_info = ("", "")
        self._state_duration_info = []
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
        """A class for the HelperDishDevice's init_device() command."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            """
            super().do()
            self._device.set_change_event("pointingState", True, False)
            self._device.set_change_event("dishMode", True, False)
            self._device.set_change_event("commandCallInfo", True, False)
            return (ResultCode.OK, "")

    pointingState = attribute(dtype=PointingState, access=AttrWriteType.READ)

    dishMode = attribute(dtype=DishMode, access=AttrWriteType.READ)
    defective = attribute(dtype=str, access=AttrWriteType.READ)
    delay = attribute(dtype=int, access=AttrWriteType.READ)

    def read_delay(self) -> int:
        """This method is used to read the attribute value for delay."""
        return self._delay

    def read_defective(self) -> str:
        """
        Returns defective status of devices

        :rtype: str
        """
        return self._defective

    commandDelayInfo = attribute(dtype=str, access=AttrWriteType.READ)

    commandCallInfo = attribute(
        dtype=(("str",),),
        access=AttrWriteType.READ,
        max_dim_x=100,
        max_dim_y=100,
    )

    obsStateTransitionDuration = attribute(
        dtype="DevString", access=AttrWriteType.READ
    )

    def read_obsStateTransitionDuration(self):
        """Read transition"""
        return json.dumps(self._state_duration_info)

    @command(
        dtype_in=str,
        doc_in="Set Obs State Duration",
    )
    def AddTransition(self, state_duration_info: str) -> None:
        """This command will set duration for dish mode such that when
        respective command for obs state is triggered then it change obs state
        after provided duration
        """
        self.logger.info(
            "Adding pointing state transitions for DishMasters Simulators"
        )
        self.logger.info(
            "PointingState transitions sequence for DishMasters Simulators \
                is: %s",
            state_duration_info,
        )

        self._state_duration_info = json.loads(state_duration_info)

    @command(
        doc_in="Reset Obs State Duration",
    )
    def ResetTransitions(self) -> None:
        """This command will reset ObsState duration which is set"""
        self.logger.info("Resetting Pointing State Duration")
        self._state_duration_info = []

    def read_commandCallInfo(self):
        """This method is used to read the attribute value for
        commandCallInfo.
        """
        return self._command_call_info

    def read_commandDelayInfo(self) -> int:
        """This method is used to read the attribute value for delay."""
        return json.dumps(self._command_delay_info)

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

    def read_pointingState(self) -> PointingState:
        """
        This method reads the pointingState of dishes.
        :rtype: PointingState
        """
        return self._pointing_state

    def read_dishMode(self) -> DishMode:
        """
        This method reads the DishMode of dishes.
        :rtype: DishMode
        """
        return self._dish_mode

    def _update_poiniting_state_in_sequence(self) -> None:
        """This method update pointing state in sequence as per
        state duration info
        """
        with tango.EnsureOmniThread():
            for poiniting_state, duration in self._state_duration_info:
                pointing_state_enum = PointingState[poiniting_state]
                self.logger.info(
                    "Sleep %s sec for pointing state %s",
                    duration,
                    poiniting_state,
                )
                time.sleep(duration)
                self.set_pointing_state(pointing_state_enum)

    def _follow_state_duration(self):
        """This method will update pointing state as per state duration"""
        thread = threading.Thread(
            target=self._update_poiniting_state_in_sequence,
        )
        thread.start()

    @command(
        dtype_in=DevEnum,
        doc_in="Assign Dish Mode.",
    )
    def SetDirectDishMode(self, argin: DishMode) -> None:
        """
        Trigger a DishMode change
        """
        self.set_dish_mode(argin)

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
        dtype_in=int,
        doc_in="pointing state to assign",
    )
    def SetDirectPointingState(self, argin: PointingState) -> None:
        """
        Trigger a PointingState change
        """
        # import debugpy; debugpy.debug_this_thread()
        value = PointingState(argin)
        if self._pointing_state != value:
            self._pointing_state = PointingState(argin)
            self.push_change_event("pointingState", self._pointing_state)

    def set_dish_mode(self, dishMode: DishMode) -> None:
        """
        This method set the Dish Mode
        """
        if self._dish_mode != dishMode:
            self._dish_mode = dishMode
            time.sleep(0.1)
            self.push_change_event("dishMode", self._dish_mode)

    def induce_fault(
        self,
        command_name: str,
    ) -> Tuple[List[ResultCode], List[str]]:
        """Induces fault into device according to given parameters

        :params:

        command_name: Name of the command for which fault is being induced
        dtype: str
        rtype: Tuple[List[ResultCode], List[str]]
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
                args=[result, command_name, fault_message],
            )
            thread.start()
            return [ResultCode.QUEUED], [""]

        return [ResultCode.OK], [""]

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

    def set_pointing_state(self, pointingState: PointingState) -> None:
        """
        This method set the Pointing State
        """
        if self._pointing_state != pointingState:
            self._pointing_state = pointingState
            self.push_change_event("pointingState", self._pointing_state)
            self.logger.info("Pointing State: %s", self._pointing_state)

    def is_Off_allowed(self) -> bool:
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                raise CommandNotAllowed(self.defective_params["error_message"])
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
        return [ResultCode.OK], [""]

    def is_Standby_allowed(self) -> bool:
        """
        This method checks if the Standby Command is allowed in current State.
        :rtype: bool
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                raise CommandNotAllowed(self.defective_params["error_message"])
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Standby(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes Standby command on Dish Master
        :rtype: Tuple
        """
        self.logger.info("Instructed Dish simulator to invoke Standby command")
        self.update_command_info(STAND_BY, "")

        if self.defective_params["enabled"]:
            return self.induce_fault("Standby")
        # Set the device state
        if self.dev_state() != DevState.STANDBY:
            self.set_state(DevState.STANDBY)
            time.sleep(0.1)
            self.push_change_event("State", self.dev_state())
        # Set the Dish Mode
        self.set_dish_mode(DishMode.STANDBY_LP)
        self.push_command_result(ResultCode.OK, "Standby")
        return ([ResultCode.OK], [""])

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
                raise CommandNotAllowed(self.defective_params["error_message"])
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

        # Set the Dish Mode
        self.set_dish_mode(DishMode.STANDBY_FP)
        self.push_command_result(ResultCode.OK, "SetStandbyFPMode")
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
                raise CommandNotAllowed(self.defective_params["error_message"])
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
        # Set the Pointing state
        if self._pointing_state != PointingState.NONE:
            self._pointing_state = PointingState.NONE
            self.push_change_event("pointingState", self._pointing_state)

        # Set the Dish ModeLP
        self.set_dish_mode(DishMode.STANDBY_LP)
        self.push_command_result(ResultCode.OK, "SetStandbyLPMode")
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
                raise CommandNotAllowed(self.defective_params["error_message"])
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
        # Set the pointing state
        if self._pointing_state != PointingState.READY:
            self._pointing_state = PointingState.READY
            self.push_change_event("pointingState", self._pointing_state)

        # Set the Dish Mode
        self.set_dish_mode(DishMode.OPERATE)
        self.push_command_result(ResultCode.OK, "SetOperateMode")
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
                raise CommandNotAllowed(self.defective_params["error_message"])
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
        # Set Dish Mode
        self.set_dish_mode(DishMode.STOW)
        self.push_command_result(ResultCode.OK, "SetStowMode")
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
                raise CommandNotAllowed(self.defective_params["error_message"])
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

        if self._pointing_state != PointingState.TRACK:
            if self._state_duration_info:
                self._follow_state_duration()
            else:
                self._pointing_state = PointingState.TRACK
                self.push_change_event("pointingState", self._pointing_state)

        # Set dish mode
        self.set_dish_mode(DishMode.OPERATE)
        self.push_command_result(ResultCode.OK, "Track")
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
                raise CommandNotAllowed(self.defective_params["error_message"])
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

        if self._pointing_state != PointingState.READY:
            if self._state_duration_info:
                self._follow_state_duration()
            else:
                self._pointing_state = PointingState.READY
                self.push_change_event("pointingState", self._pointing_state)
                self.logger.info("Pointing State: %s", self._pointing_state)

        # Set dish mode
        self.set_dish_mode(DishMode.OPERATE)
        self.push_command_result(ResultCode.OK, "TrackStop")
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
                raise CommandNotAllowed(self.defective_params["error_message"])
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
        # Dish Mode Not Applicable.
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
                raise CommandNotAllowed(self.defective_params["error_message"])
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
        self.logger.info("Processing Configure command")
        # to record the command data
        self.logger.info(
            "Instructed Dish simulator to invoke Configure command"
        )
        self.update_command_info(CONFIGURE, argin)
        if self.defective_params["enabled"]:
            return self.induce_fault("Configure")
        return [ResultCode.OK], [""]

    def is_ConfigureBand1_allowed(self) -> bool:
        """
        This method checks if the ConfigureBand1 command is allowed in current
        State.
        :rtype: bool
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                raise CommandNotAllowed(self.defective_params["error_message"])
        return True

    @command(
        dtype_in=("DevString"),
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ConfigureBand1(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes ConfigureBand1 command on  Dish Master
        """
        self.logger.info(
            "Instructed Dish simulator to invoke ConfigureBand1 command"
        )

        if self.defective_params["enabled"]:
            return self.induce_fault("ConfigureBand1")

        # Set dish mode
        self.set_dish_mode(DishMode.CONFIG)
        self.push_command_result(ResultCode.OK, "ConfigureBand1")
        return ([ResultCode.OK], [""])

    def is_ConfigureBand2_allowed(self) -> bool:
        """
        This method checks if the ConfigureBand2 Command is allowed in current
        State.
        :rtype: bool
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                raise CommandNotAllowed(self.defective_params["error_message"])
        return True

    @command(
        dtype_in=("DevString"),
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ConfigureBand2(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes ConfigureBand2 command on Dish Master
        :rtype: tuple
        """
        self.logger.info("Processing ConfigureBand2 Command")
        # to record the command data
        self.update_command_info(CONFIGURE_BAND_2, argin)
        if self.defective_params["enabled"]:
            return self.induce_fault("ConfigureBand2")

        # Set the Dish Mode
        current_dish_mode = self._dish_mode
        self.set_dish_mode(DishMode.CONFIG)
        thread = threading.Thread(
            target=self.update_dish_mode,
            args=[current_dish_mode, CONFIGURE],
        )
        thread.start()
        self.push_command_result(ResultCode.OK, "ConfigureBand2")
        return ([ResultCode.OK], [""])

    def update_dish_mode(self, value, command_name: str = ""):
        """Sets the dish mode back to original state."""
        with tango.EnsureOmniThread():
            if command_name in self._command_delay_info:
                delay_value = self._command_delay_info[command_name]
            time.sleep(delay_value)
            self.logger.info(
                "Sleep %s for command %s ", delay_value, command_name
            )
        self.set_dish_mode(value)

    def update_pointing_state(self, value, command_name):
        """Sets the dish mode back to original state."""
        with tango.EnsureOmniThread():
            if command_name in self._command_delay_info:
                delay_value = self._command_delay_info[command_name]
                time.sleep(delay_value)
            self.logger.info(
                "Sleep %s for command %s ", delay_value, command_name
            )
        self.set_pointing_state(value)

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

    def is_ConfigureBand3_allowed(self) -> bool:
        """
        This method checks if the ConfigureBand3 Command is allowed in current
        State.
        :rtype:bool
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                raise CommandNotAllowed(self.defective_params["error_message"])
        return True

    @command(
        dtype_in=("DevString"),
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ConfigureBand3(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes ConfigureBand3 command on  Dish Master
        """
        self.logger.info("Processing ConfigureBand3 Command")

        if self.defective_params["enabled"]:
            return self.induce_fault("ConfigureBand3")

        # Set dish mode
        self.set_dish_mode(DishMode.CONFIG)
        self.push_command_result(ResultCode.OK, "ConfigureBand3")
        return ([ResultCode.OK], [""])

    def is_ConfigureBand4_allowed(self) -> bool:
        """
        This method checks if the ConfigureBand4 Command is allowed in current
        State.
        :rtype: bool
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                raise CommandNotAllowed(self.defective_params["error_message"])
        return True

    @command(
        dtype_in=("DevString"),
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ConfigureBand4(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes ConfigureBand4 command on Dish Master
        """
        self.logger.info("Processing ConfigureBand4 Command")

        if self.defective_params["enabled"]:
            return self.induce_fault("ConfigureBand4")

        # Set dish mode
        self.set_dish_mode(DishMode.CONFIG)
        self.push_command_result(ResultCode.OK, "ConfigureBand4")
        return ([ResultCode.OK], [""])

    def is_ConfigureBand5a_allowed(self) -> bool:
        """
        This method checks if the ConfigureBand5a Command is allowed in current
        State.
        :rtype:bool
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                raise CommandNotAllowed(self.defective_params["error_message"])
        return True

    @command(
        dtype_in=("DevString"),
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ConfigureBand5a(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes ConfigureBand5a command on Dish Master
        """
        self.logger.info("Processing ConfigureBand5a Command")

        if self.defective_params["enabled"]:
            return self.induce_fault("ConfigureBand5a")
        # Set dish mode
        self.set_dish_mode(DishMode.CONFIG)
        self.push_command_result(ResultCode.OK, "ConfigureBand5a")
        return ([ResultCode.OK], [""])

    def is_ConfigureBand5b_allowed(self) -> bool:
        """
        This method checks if the ConfigureBand5b Command is allowed in current
        State.
        :rtype:bool
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                raise CommandNotAllowed(self.defective_params["error_message"])
        return True

    @command(
        dtype_in=("DevString"),
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ConfigureBand5b(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes ConfigureBand5b command on Dish Master
        """
        self.logger.info("Processing ConfigureBand5b Command")

        if self.defective_params["enabled"]:
            return self.induce_fault("ConfigureBand5b")
        # Set dish mode
        self.set_dish_mode(DishMode.CONFIG)
        self.push_command_result(ResultCode.OK, "ConfigureBand5b")
        return ([ResultCode.OK], [""])

    def is_Slew_allowed(self) -> bool:
        """
        This method checks if the Slew command is allowed in current State.
        :rtype:bool
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                raise CommandNotAllowed(self.defective_params["error_message"])
        return True

    @command(
        dtype_in=("DevVoid"),
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Slew(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes Slew command on Dish Master
        """
        self.logger.info("Processing Slew Command")
        # to record the command data
        self.update_command_info(SLEW)
        if self.defective_params["enabled"]:
            return self.induce_fault("Slew")

        if self._pointing_state != PointingState.SLEW:
            self._pointing_state = PointingState.SLEW
            self.push_change_event("pointingState", self._pointing_state)
        return ([ResultCode.OK], [""])

    @command(
        dtype_in=("DevVoid"),
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def StartCapture(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes StartCapture command on Dish Master
        """
        # TBD: Dish mode changedoc_out="(ReturnType, 'DevVoid')",
        return ([ResultCode.OK], [""])

    @command(
        dtype_in=("DevVoid"),
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetMaintenanceMode(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method sets the Maintainance Mode for the dish
        """
        # TBD: Dish mode change
        return ([ResultCode.OK], [""])

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
                raise CommandNotAllowed(self.defective_params["error_message"])
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

    def is_Reset_allowed(self) -> bool:
        """
        This method checks if the Reset command is allowed in current State.
        :rtype:bool
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                raise CommandNotAllowed(self.defective_params["error_message"])
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Reset(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes Reset command on Dish Master
        :rtype:tuple
        """
        self.logger.info("Processing Reset Command")
        # to record the command data
        self.update_command_info(RESET)
        if self.defective_params["enabled"]:
            return self.induce_fault("Reset")

            # TBD: Add your dish mode change logic here if required
        return ([ResultCode.OK], [""])


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
    return run((HelperDishDevice,), args=args, **kwargs)


if __name__ == "__main__":
    main()
