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

from ska_tmc_common.enum import DishMode, PointingState
from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice

from .constants import (
    ABORT,
    ABORT_COMMANDS,
    CONFIGURE,
    RESTART,
    SET_OPERATE_MODE,
    SET_STANDBY_FP_MODE,
    SET_STANDBY_LP_MODE,
    SET_STOW_MODE,
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
        self._pointing_state = PointingState.NONE
        self._dish_mode = DishMode.STANDBY_LP
        self._command_delay_info = {
            CONFIGURE: 2,
            ABORT: 2,
            RESTART: 2,
        }
        self._command_call_info = []
        self._command_info = ("", "")

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

    commandDelayInfo = attribute(dtype=str, access=AttrWriteType.READ)

    commandCallInfo = attribute(
        dtype=(("str",),),
        access=AttrWriteType.READ,
        max_dim_x=100,
        max_dim_y=100,
    )

    def read_commandCallInfo(self):
        """This method is used to read the attribute value for commandCallInfo."""

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
        self.logger.info("Setting the Delay value to : %s", command_delay_info)
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
        self.logger.info("Resetting Command Delay")
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
        self._command_call_info.clear()
        self.push_change_event("commandCallInfo", self._command_call_info)
        self.logger.info("CommandCallInfo updates are pushed")

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

    @command(
        dtype_in=DevEnum,
        doc_in="Assign Dish Mode.",
    )
    def SetDirectDishMode(self, argin: DishMode) -> None:
        """
        Trigger a DishMode change
        """
        if not self._defective:
            self.set_dish_mode(argin)

    @command(
        dtype_in=int,
        doc_in="pointing state to assign",
    )
    def SetDirectPointingState(self, argin: PointingState) -> None:
        """
        Trigger a PointingState change
        """
        # import debugpy; debugpy.debug_this_thread()
        if not self._defective:
            value = PointingState(argin)
            if self._pointing_state != value:
                self._pointing_state = PointingState(argin)
                self.push_change_event("pointingState", self._pointing_state)

    def set_dish_mode(self, dishMode: DishMode) -> None:
        """
        This method set the Dish Mode
        """
        if not self._defective:
            if self._dish_mode != dishMode:
                self._dish_mode = dishMode
                self.push_change_event("dishMode", self._dish_mode)

    def set_pointing_state(self, pointingState: PointingState) -> None:
        """
        This method set the Pointing State
        """
        if not self._defective:
            if self._pointing_state != pointingState:
                self._pointing_state = pointingState
                self.push_change_event("pointingState", self._pointing_state)

    def is_Standby_allowed(self) -> bool:
        """
        This method checks if the Standby Command is allowed in current State.
        :rtype: bool
        """
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
        self.update_command_info(STAND_BY, "")

        # Set the device state
        if not self._defective:
            if self.dev_state() != DevState.STANDBY:
                self.set_state(DevState.STANDBY)
                time.sleep(0.1)
                self.push_change_event("State", self.dev_state())
            # Set the Dish Mode
            self.set_dish_mode(DishMode.STANDBY_LP)
            return ([ResultCode.OK], [""])

        return [ResultCode.FAILED], [
            "Device is Defective, cannot process command."
        ]

    def is_SetStandbyFPMode_allowed(self) -> bool:
        """
        This method checks if the is_SetStandbyFPMode_allowed Command is allowed in current
        State.
        :rtype:bool
        """
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
        self.update_command_info(SET_STANDBY_FP_MODE, "")

        # import debugpy; debugpy.debug_this_thread()'
        if not self._defective:
            self.logger.info("Processing SetStandbyFPMode Command")
            # Set the Device State
            if self.dev_state() != DevState.STANDBY:
                self.set_state(DevState.STANDBY)
                time.sleep(0.1)
                self.push_change_event("State", self.dev_state())
            # Set the Dish Mode
            self.set_dish_mode(DishMode.STANDBY_FP)
            return ([ResultCode.OK], [""])

        return [ResultCode.FAILED], [
            "Device is Defective, cannot process command."
        ]

    def is_SetStandbyLPMode_allowed(self) -> bool:
        """
        This method checks if the is_SetStandbyLPMode_allowed Command is allowed in current
        State.
        :rtype: bool
        """
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
        self.update_command_info(SET_STANDBY_LP_MODE, "")

        if not self._defective:
            self.logger.info("Processing SetStandbyLPMode Command")
            # Set the device state
            if self.dev_state() != DevState.STANDBY:
                self.set_state(DevState.STANDBY)
                time.sleep(0.1)
                self.push_change_event("State", self.dev_state())
            # Set the Pointing state
            if self._pointing_state != PointingState.NONE:
                self._pointing_state = PointingState.NONE
                self.push_change_event("pointingState", self._pointing_state)
            # Set the Dish Mode
            self.set_dish_mode(DishMode.STANDBY_LP)
            return ([ResultCode.OK], [""])

        return [ResultCode.FAILED], [
            "Device is Defective, cannot process command."
        ]

    def is_SetOperateMode_allowed(self) -> bool:
        """
        This method checks if the SetOperateMode Command is allowed in current
        State.
        :rtype:bool
        """
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
        self.update_command_info(SET_OPERATE_MODE, "")

        if not self._defective:
            self.logger.info("Processing SetOperateMode Command")
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
            return ([ResultCode.OK], [""])

        return [ResultCode.FAILED], [
            "Device is Defective, cannot process command."
        ]

    def is_SetStowMode_allowed(self) -> bool:
        """
        This method checks if the SetStowMode Command is allowed in current
        State.
        :rtype: bool
        """
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
        self.update_command_info(SET_STOW_MODE, "")

        if not self._defective:
            self.logger.info("Processing SetStowMode Command")
            # Set device state
            if self.dev_state() != DevState.DISABLE:
                self.set_state(DevState.DISABLE)
                time.sleep(0.1)
                self.push_change_event("State", self.dev_state())
            # Set dish mode
            self.set_dish_mode(DishMode.STOW)
            return ([ResultCode.OK], [""])

        return [ResultCode.FAILED], [
            "Device is Defective, cannot process command."
        ]

    def is_Track_allowed(self) -> bool:
        """
        This method checks if the Track Command is allowed in current
        State.
        :rtype: bool
        """
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
        self.update_command_info(TRACK, "")

        if not self._defective:
            self.logger.info("Processing Track Command")
            if self._pointing_state != PointingState.TRACK:
                self._pointing_state = PointingState.TRACK
                self.push_change_event("pointingState", self._pointing_state)
            # Set dish mode
            self.set_dish_mode(DishMode.OPERATE)
            return ([ResultCode.OK], [""])

        return [ResultCode.FAILED], [
            "Device is Defective, cannot process command."
        ]

    def is_TrackStop_allowed(self) -> bool:
        """
        This method checks if the TrackStop Command is allowed in current
        State.
        :rtype: bool
        """
        return True

    @command(
        dtype_in="DevVoid",
        doc_out="(ReturnType, 'DevVoid')",
    )
    def TrackStop(self) -> None:
        """
        This method invokes TrackStop command on  Dish Master
        """
        self.update_command_info(TRACK_STOP, "")

        if not self._defective:
            self.logger.info("Processing TrackStop Command")
            if self._pointing_state != PointingState.READY:
                self._pointing_state = PointingState.READY
                self.push_change_event("pointingState", self._pointing_state)
                self.logger.info("Pointing State: %s", self._pointing_state)
            # Set dish mode
            self.set_dish_mode(DishMode.OPERATE)
            return ([ResultCode.OK], [""])

        return [ResultCode.FAILED], [
            "Device is Defective, cannot process command."
        ]

    def is_AbortCommands_allowed(self) -> bool:
        """
        This method checks if the AbortCommands command is allowed in current
        State.
        :rtype: bool
        """
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
        self.update_command_info(ABORT_COMMANDS, "")

        self.logger.info("Abort Completed")
        # Dish Mode Not Applicable.
        return ([ResultCode.OK], [""])

    def is_Configure_allowed(self) -> bool:
        """
        This method checks if the Configure Command is allowed in current
        State.
        :rtype: bool
        """
        return True

    @command(
        dtype_in=("DevString"),
        doc_out="(ReturnType, 'DevVarLongStringArray')",
    )
    def Configure(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes Configure command on  Dish Master
        :rtype: tuple
        """
        # to record the command data
        self.update_command_info(CONFIGURE, argin)

        if not self._defective:
            self.logger.info("Processing Configure command")
            return [ResultCode.OK], ["Configure completed"]
        return [ResultCode.FAILED], ["Device defective. Configure Failed."]

    def is_ConfigureBand1_allowed(self) -> bool:
        """
        This method checks if the ConfigureBand1 command is allowed in current
        State.
        :rtype: bool
        """
        return True

    @command(
        dtype_in=("DevString"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def ConfigureBand1(self, argin: str) -> None:
        """
        This method invokes ConfigureBand1 command on  Dish Master
        """
        if not self._defective:
            self.logger.info("Processing ConfigureBand1")
            # Set dish mode
            self.set_dish_mode(DishMode.CONFIG)

    def is_ConfigureBand2_allowed(self) -> bool:
        """
        This method checks if the ConfigureBand2 Command is allowed in current
        State.
        :rtype: bool
        """
        return True

    @command(
        dtype_in=("DevString"),
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'DevVarLongStringArray')",
    )
    def ConfigureBand2(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes ConfigureBand2 command on Dish Master
        :rtype: tuple
        """
        current_dish_mode = self._dish_mode
        if not self._defective:
            self.logger.info("Processing ConfigureBand2")
            self.set_dish_mode(DishMode.CONFIG)
            thread = threading.Thread(
                target=self.update_dish_mode,
                args=[current_dish_mode, CONFIGURE],
            )
            thread.start()
            return ([ResultCode.OK], [""])

        return [ResultCode.FAILED], [
            "Device is Defective, cannot process command."
        ]

    def update_dish_mode(self, value, command_name):
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
        self.logger.info("Recording the command data")
        self._command_info = (command_name, command_input)
        self.logger.info(
            "Updated command_info value is %s", self._command_info
        )
        self._command_call_info.append(self._command_info)
        self.logger.info(
            "Updated command_call_info value is %s", self._command_call_info
        )
        self.push_change_event("commandCallInfo", self._command_call_info)
        self.logger.info("CommandCallInfo updates are pushed")

    def is_ConfigureBand3_allowed(self) -> bool:
        """
        This method checks if the ConfigureBand3 Command is allowed in current
        State.
        :rtype:bool
        """
        return True

    @command(
        dtype_in=("DevString"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def ConfigureBand3(self, argin: str) -> None:
        """
        This method invokes ConfigureBand3 command on  Dish Master
        """
        if not self._defective:
            self.logger.info("Processing ConfigureBand3")
            # Set dish mode
            self.set_dish_mode(DishMode.CONFIG)

    def is_ConfigureBand4_allowed(self) -> bool:
        """
        This method checks if the ConfigureBand4 Command is allowed in current
        State.
        :rtype: bool
        """
        return True

    @command(
        dtype_in=("DevString"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def ConfigureBand4(self, argin: str) -> None:
        """
        This method invokes ConfigureBand4 command on Dish Master
        """
        if not self._defective:
            self.logger.info("Processing ConfigureBand4")
            # Set dish mode
            self.set_dish_mode(DishMode.CONFIG)

    def is_ConfigureBand5a_allowed(self) -> bool:
        """
        This method checks if the ConfigureBand5a Command is allowed in current
        State.
        :rtype:bool
        """
        return True

    @command(
        dtype_in=("DevString"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def ConfigureBand5a(self, argin: str) -> None:
        """
        This method invokes ConfigureBand5a command on Dish Master
        """
        if not self._defective:
            self.logger.info("Processing ConfigureBand5a")
            # Set dish mode
            self.set_dish_mode(DishMode.CONFIG)

    def is_ConfigureBand5b_allowed(self) -> bool:
        """
        This method checks if the ConfigureBand5b Command is allowed in current
        State.
        :rtype:bool
        """
        return True

    @command(
        dtype_in=("DevString"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def ConfigureBand5b(self, argin: str) -> None:
        """
        This method invokes ConfigureBand5b command on Dish Master
        """
        if not self._defective:
            self.logger.info("Processing ConfigureBand5")
            # Set dish mode
            self.set_dish_mode(DishMode.CONFIG)

    def is_Slew_allowed(self) -> bool:
        """
        This method checks if the Slew command is allowed in current State.
        :rtype:bool
        """
        return True

    @command(
        dtype_in=("DevVarDoubleArray"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def Slew(self) -> None:
        """
        This method invokes Slew command on Dish Master
        """
        if not self._defective:
            if self._pointing_state != PointingState.SLEW:
                self._pointing_state = PointingState.SLEW
                self.push_change_event("pointingState", self._pointing_state)
            # TBD: Dish mode change

    @command(
        dtype_in=("DevVoid"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def StartCapture(self) -> None:
        """
        This method invokes StartCapture command on Dish Master
        """
        # TBD: Dish mode change

    @command(
        dtype_in=("DevVoid"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def SetMaintenanceMode(self) -> None:
        """
        This method sets the Maintainance Mode for the dish
        """
        # TBD: Dish mode change

    def is_Scan_allowed(self) -> bool:
        """
        This method checks if the Scan Command is allowed in current State.
        :rtype:bool
        """
        return True

    @command(
        dtype_in=("DevVoid"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def Scan(self) -> None:
        """
        This method invokes Scan command on Dish Master
        """
        # TBD: Dish mode change
        self.logger.info("Processing Scan")

    def is_Reset_allowed(self) -> bool:
        """
        This method checks if the Reset command is allowed in current State.
        :rtype:bool
        """
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
        # TBD: Dish mode change
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
