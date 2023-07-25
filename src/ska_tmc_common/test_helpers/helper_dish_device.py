"""
This module implements the Helper Dish Device for testing an integrated TMC
"""
import json
import threading
import time
from typing import List, Tuple

from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from tango import AttrWriteType, DevEnum, DevState
from tango.server import attribute, command, run

from ska_tmc_common import CommandNotAllowed, FaultType
from ska_tmc_common.enum import DishMode, PointingState
from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice


# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument
class HelperDishDevice(HelperBaseDevice):
    """A device exposing commands and attributes of the Dish device."""

    def init_device(self):
        super().init_device()
        self._delay = 2
        self._pointing_state = PointingState.NONE
        self._dish_mode = DishMode.STANDBY_LP
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
            return (ResultCode.OK, "")

    pointingState = attribute(dtype=PointingState, access=AttrWriteType.READ)
    dishMode = attribute(dtype=DishMode, access=AttrWriteType.READ)
    defective = attribute(dtype=str, access=AttrWriteType.READ)

    def read_defective(self) -> str:
        """
        Returns defective status of devices

        :rtype: str
        """
        return self.defective_params

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
        if not self.defective_params["enabled"]:
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
        command_id = f"{time.time()}-{command}"
        if exception:
            command_result = (command_id, exception)
            self.push_change_event("longRunningCommandResult", command_result)
        command_result = (command_id, json.dumps(result))
        self.push_change_event("longRunningCommandResult", command_result)

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

        if self.defective_params["enabled"]:
            return self.induce_fault("SetStandbyFPMode")
        self.logger.info("Processing SetStandbyFPMode Command")
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
        if self.defective_params["enabled"]:
            return self.induce_fault("SetStandbyLPMode")
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
        if self.defective_params["enabled"]:
            return self.induce_fault("SetOperateMode")
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
        if self.defective_params["enabled"]:
            return self.induce_fault("SetStowMode")
        self.logger.info("Processing SetStowMode Command")

        # Set device state
        if self.dev_state() != DevState.DISABLE:
            self.set_state(DevState.DISABLE)
            self.push_change_event("State", self.dev_state())
            time.sleep(0.1)
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
        if self.defective_params["enabled"]:
            return self.induce_fault("Track")
        self.logger.info("Processing Track Command")

        if self._pointing_state != PointingState.TRACK:
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
        if self.defective_params["enabled"]:
            return self.induce_fault("TrackStop")
        self.logger.info("Processing TrackStop Command")

        if self._pointing_state != PointingState.READY:
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
        if self.defective_params["enabled"]:
            return self.induce_fault("Configure")

        self.logger.info("Processing Configure command")
        return [ResultCode.OK], ["Configure completed"]

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
        if self.defective_params["enabled"]:
            return self.induce_fault("ConfigureBand1")
        self.logger.info("Processing ConfigureBand1 Command")

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
        if self.defective_params["enabled"]:
            return self.induce_fault("ConfigureBand2")
        self.logger.info("Processing ConfigureBand2 Command")

        # Set the Dish Mode
        self.set_dish_mode(DishMode.CONFIG)
        current_dish_mode = self._dish_mode
        thread = threading.Thread(
            target=self.update_dish_mode,
            args=[current_dish_mode],
        )
        thread.start()
        self.push_command_result(ResultCode.OK, "ConfigureBand2")
        return ([ResultCode.OK], [""])

    def update_dish_mode(self, value) -> None:
        """Sets the dish mode back to original state."""
        time.sleep(self._delay)
        self.set_dish_mode(value)

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
        if self.defective_params["enabled"]:
            return self.induce_fault("ConfigureBand3")
        self.logger.info("Processing ConfigureBand3 Command")

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
        if self.defective_params["enabled"]:
            return self.induce_fault("ConfigureBand5b")

        if not self.defective_params["enabled"]:
            if self._pointing_state != PointingState.SLEW:
                self._pointing_state = PointingState.SLEW
                self.push_change_event("pointingState", self._pointing_state)
                return ([ResultCode.OK], [""])
        return (
            [ResultCode.FAILED],
            ["Device is defective, cannot process command."],
        )

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
        if self.defective_params["enabled"]:
            return self.induce_fault("Scan")

        if not self._defective:
            # TBD: Add your dish mode change logic here if required
            self.logger.info("Processing Scan")
            return ([ResultCode.OK], [""])

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]

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
        if self.defective_params["enabled"]:
            return self.induce_fault("Reset")

        if not self._defective:
            # TBD: Add your dish mode change logic here if required
            return ([ResultCode.OK], [""])

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]


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
