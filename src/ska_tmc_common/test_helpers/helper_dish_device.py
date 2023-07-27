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
        dtype_in=int,
        doc_in="Set Delay",
    )
    def SetDelay(self, value: int) -> None:
        """Update delay value"""
        self.logger.info("Setting the Delay value to : %s", value)
        self._delay = value

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
        command_id = f"{time.time()}-{command}"
        if exception:
            command_result = (command_id, exception)
            self.push_change_event("longRunningCommandResult", command_result)
        command_result = (command_id, json.dumps(result))
        self.push_change_event("longRunningCommandResult", command_result)

    def post_command_failed(self, command_name: str) -> None:
        """
        This method executes the instructions after failure of given
        command
        :params:

        command_name: Name of the command
        dtype: str
        rtype: None
        """
        self.logger.info(" %s command failed", command_name)
        self.push_command_result(ResultCode.FAILED, command_name)
        return ([ResultCode.FAILED], [f"{command_name} command failed"])

    def post_command_success(self, command_name: str) -> None:
        """
        This method executes the instructions after success of given
        command
        :params:

        command_name: Name of the command
        dtype: str
        rtype: None
        """
        self.push_command_result(ResultCode.OK, command_name)
        self.logger.info("Successfully processed %s command", command_name)
        return ([ResultCode.OK], [""])

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
        if self.dev_state() == DevState.STANDBY:
            # Set the Dish Mode
            self.set_dish_mode(DishMode.STANDBY_LP)
            return self.post_command_success(command_name="Standby")

        return self.post_command_failed(command_name="Standby")

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
        if self.defective_params["enabled"]:
            return self.induce_fault("SetStandbyFPMode")
        if self.dev_state() != DevState.STANDBY:
            self.set_state(DevState.STANDBY)
            time.sleep(0.1)
            self.push_change_event("State", self.dev_state())
        if self.dev_state() == DevState.STANDBY:
            # Set the Dish Mode
            self.set_dish_mode(DishMode.STANDBY_FP)
            return self.post_command_success(command_name="SetStandbyFPMode")

        return self.post_command_failed(command_name="SetStandbyFPMode")

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
        self.logger.info("Processing SetStandbyLPMode Command")

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
        if self._pointing_state == PointingState.NONE:
            # Set the Dish ModeLP
            self.set_dish_mode(DishMode.STANDBY_LP)
            return self.post_command_success(command_name="SetStandbyLPMode")

        return self.post_command_failed(command_name="SetStandbyLPMode")

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
        self.logger.info("Processing SetOperateMode Command")

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
        if self._pointing_state == PointingState.READY:
            # Set the Dish Mode
            self.set_dish_mode(DishMode.OPERATE)
            return self.post_command_success(command_name="SetOperateMode")

        return self.post_command_failed(command_name="SetOperateMode")

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
        self.logger.info("Processing SetStowMode Command")
        if self.defective_params["enabled"]:
            return self.induce_fault("SetStowMode")

        # Set device state
        if self.dev_state() != DevState.DISABLE:
            self.set_state(DevState.DISABLE)
            time.sleep(0.1)
            self.push_change_event("State", self.dev_state())
        if self.dev_state() == DevState.DISABLE:
            self.set_dish_mode(DishMode.STOW)
            return self.post_command_success(command_name="SetStowMode")

        return self.post_command_failed(command_name="SetStowMode")

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
        self.logger.info("Processing Track Command")

        if self.defective_params["enabled"]:
            return self.induce_fault("Track")

        if self._pointing_state != PointingState.TRACK:
            self._pointing_state = PointingState.TRACK
            self.push_change_event("pointingState", self._pointing_state)

        if self._pointing_state == PointingState.TRACK:
            # Set dish mode
            self.set_dish_mode(DishMode.OPERATE)
            return self.post_command_success(command_name="Track")

        return self.post_command_failed(command_name="Track")

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
        self.logger.info("Processing TrackStop Command")

        if self.defective_params["enabled"]:
            return self.induce_fault("TrackStop")

        if self._pointing_state != PointingState.READY:
            self._pointing_state = PointingState.READY
            self.push_change_event("pointingState", self._pointing_state)

        if self._pointing_state == PointingState.READY:
            # Set dish mode
            self.set_dish_mode(DishMode.OPERATE)
            return self.post_command_success(command_name="TrackStop")

        return self.post_command_failed(command_name="TrackStop")

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
        self.logger.info("Processing Configure command")

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
        self.logger.info("Processing ConfigureBand1 Command")

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

        if self.defective_params["enabled"]:
            return self.induce_fault("ConfigureBand2")

        # Set the Dish Mode
        current_dish_mode = self._dish_mode
        self.set_dish_mode(DishMode.CONFIG)
        thread = threading.Thread(
            target=self.update_dish_mode,
            args=[current_dish_mode],
        )
        thread.start()
        return self.post_command_success(command_name="ConfigureBand2")

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
