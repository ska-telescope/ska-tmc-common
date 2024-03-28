# pylint: disable=C0302
"""
This module implements the Helper Dish Leaf Node Device for testing an
integrated TMC.
"""
import json
import threading
import time
from typing import List, Tuple, Union

import tango
from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from tango import AttrWriteType, Database, DevState
from tango.server import attribute, command, run

from ska_tmc_common import CommandNotAllowed, FaultType
from ska_tmc_common.enum import DishMode, PointingState
from ska_tmc_common.test_helpers.constants import (
    ABORT,
    ABORT_COMMANDS,
    CONFIGURE,
    END_SCAN,
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
from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice


# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument,too-many-public-methods,invalid-name
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
        self._dish_kvalue_validation_result = str(int(ResultCode.STARTED))
        self._dish_mode = DishMode.STANDBY_LP
        self._pointing_state = PointingState.NONE

    # pylint: disable=protected-access
    class InitCommand(SKABaseDevice.InitCommand):
        """A class for the HelperDishLNDevice's init_device() command."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            :return: ResultCode and message
            """
            super().do()
            self._device._dishln_name = self._device.get_name()
            self._device.set_change_event("commandCallInfo", True, False)
            self._device.set_change_event("isSubsystemAvailable", True, False)
            self._device.set_change_event(
                "kValueValidationResult", True, False
            )
            self._device.set_change_event(
                "longRunningCommandResult", True, False
            )
            self._device.set_change_event("actualPointing", True, False)
            self._device.set_change_event("pointingState", True, False)
            self._device.set_change_event("dishMode", True, False)
            self._device.op_state_model.perform_action("component_on")
            self._device.push_dish_kvalue_val_result_after_initialization()
            return (ResultCode.OK, "")

    defective = attribute(dtype=str, access=AttrWriteType.READ)
    delay = attribute(dtype=int, access=AttrWriteType.READ)
    actualPointing = attribute(dtype=str, access=AttrWriteType.READ)
    isSubsystemAvailable = attribute(dtype=bool, access=AttrWriteType.READ)
    kValueValidationResult = attribute(dtype=str, access=AttrWriteType.READ)
    pointingState = attribute(dtype=PointingState, access=AttrWriteType.READ)
    dishMode = attribute(dtype=DishMode, access=AttrWriteType.READ)

    # pylint: enable=protected-access
    def read_kValueValidationResult(self) -> str:
        """
        Get the k-value validation result.
        :return: kValue validation result
        :rtype:str
        """
        return self._dish_kvalue_validation_result

    @attribute(
        dtype=int,
        access=AttrWriteType.READ_WRITE,
        memorized=True,
        hw_memorized=True,
    )
    def kValue(self) -> int:
        """
        This attribute is used for storing dish kvalue
        into tango DB.Made this attribute memorized so that when device
        restart then previous set kvalue will be used validation.
        :return: kvalue
        """
        return self._kvalue

    @kValue.write
    def kValue(self, kvalue: str) -> None:
        """Set memorized dish vcc map
        :param kvalue: dish vcc config json string
        :type str
        """
        self._kvalue = kvalue

    def read_delay(self) -> int:
        """
        This method is used to read the attribute value for delay.
        :return: delay
        """
        return self._delay

    def read_defective(self) -> str:
        """
        Returns defective status of devices
        :return: defective status of devices
        :rtype: str
        """
        return json.dumps(self.defective_params)

    def read_actualPointing(self) -> str:
        """
        Read method for actual pointing.
        :return: actual pointing value
        """
        return json.dumps(self._actual_pointing)

    def read_isSubsystemAvailable(self) -> bool:
        """
        Returns avalability status for the leaf nodes devices
        :return: boolean value for attribute isSubsystemAvailable
        :rtype: bool
        """
        return self._isSubsystemAvailable

    def read_pointingState(self) -> PointingState:
        """
        This method reads the pointingState of dishes.
        :return: pointingState of dishes
        :rtype: PointingState
        """
        return self._pointing_state

    def read_dishMode(self) -> DishMode:
        """
        This method reads the DishMode of dishes.
        :return: DishMode of dishes
        :rtype: DishMode
        """
        return self._dish_mode

    def set_dish_mode(self, dishMode: DishMode) -> None:
        """
        This method set the Dish Mode
        """
        self._dish_mode = dishMode
        time.sleep(0.1)
        self.push_change_event("dishMode", self._dish_mode)

    def set_pointing_state(self, pointingState: PointingState) -> None:
        """
        This method set the Pointing State
        """
        self._pointing_state = pointingState
        self.push_change_event("pointingState", self._pointing_state)
        self.logger.info("Pointing State: %s", self._pointing_state)

    def update_dish_mode(
        self, value: DishMode, command_name: str = ""
    ) -> None:
        """Sets the dish mode back to original state.

        :param value: Dish Mode to update.
        :value dtype: DishMode
        :param command_name: Command name
        :command_name dtype: str

        :rtype: None
        """
        with tango.EnsureOmniThread():
            if command_name in self._command_delay_info:
                delay_value = self._command_delay_info[command_name]
            time.sleep(delay_value)
            self.logger.info(
                "Sleep %s for command %s ", delay_value, command_name
            )
        self.set_dish_mode(value)

    def update_pointing_state(
        self, value: PointingState, command_name: str
    ) -> None:
        """Sets the dish mode back to original state.

        :param value: Pointing state to update.
        :value dtype: PointingState
        :param command_name: Command name
        :command_name dtype: str

        :rtype: None
        """
        with tango.EnsureOmniThread():
            if command_name in self._command_delay_info:
                delay_value = self._command_delay_info[command_name]
                time.sleep(delay_value)
            self.logger.info(
                "Sleep %s for command %s ", delay_value, command_name
            )
        self.set_pointing_state(value)

    commandDelayInfo = attribute(dtype=str, access=AttrWriteType.READ)

    commandCallInfo = attribute(
        dtype=(("str",),),
        access=AttrWriteType.READ,
        max_dim_x=1000,
        max_dim_y=1000,
    )

    def _update_pointing_state_in_sequence(self) -> None:
        """This method update pointing state in sequence as per
        state duration info
        """
        for pointing_state, duration in self._state_duration_info:
            pointing_state_enum = PointingState[pointing_state]
            self.logger.info(
                "Sleep %s sec for pointing state %s",
                duration,
                pointing_state,
            )
            time.sleep(duration)
            with tango.EnsureOmniThread():
                self.set_pointing_state(pointing_state_enum)

    def _follow_state_duration(self):
        """This method will update pointing state as per state duration"""
        thread = threading.Thread(
            target=self._update_pointing_state_in_sequence,
        )
        thread.start()

    @command(
        dtype_in=str,
        doc_in="(ReturnType, 'ResultCode')",
    )
    def SetDirectkValueValidationResult(self, result_code: str) -> None:
        """Set the kValuValidationResult
        :argin dtype: str
        :rtype:None
        """
        self._dish_kvalue_validation_result = result_code
        self.push_change_event(
            "kValueValidationResult", self._dish_kvalue_validation_result
        )
        self.logger.debug(
            "kValueValidationResult set to: %s",
            self._dish_kvalue_validation_result,
        )

    def set_offset(self, cross_elevation: float, elevation: float) -> None:
        """Sets the offset for Dish."""
        self._offset["off_xel"] = cross_elevation
        self._offset["off_el"] = elevation

    def read_commandCallInfo(self):
        """
        This method is used to read the attribute value for
        commandCallInfo.
        :return: command_call_info value
        """
        return self._command_call_info

    def read_commandDelayInfo(self) -> str:
        """
        This method is used to read the attribute value for delay.
        :return: command_delay_infp value
        """
        return json.dumps(self._command_delay_info)

    def push_dish_kvalue_validation_result(self):
        """Push Dish k-value Validation result event
        If memorized k-value already set then push Result Code as OK
        else push result code event as UNKNOWN
        """
        if self._kvalue:
            self.logger.info("Memorized k-value=%s", self._kvalue)
            self._dish_kvalue_validation_result = str(int(ResultCode.OK))
        else:
            self._dish_kvalue_validation_result = str(int(ResultCode.UNKNOWN))

        self.logger.info(
            "Push Dish kvalue Validation Result as %s",
            self._dish_kvalue_validation_result,
        )
        self.push_change_event(
            "kValueValidationResult",
            str(int(self._dish_kvalue_validation_result)),
        )

    def push_dish_kvalue_val_result_after_initialization(self):
        """This method gets invoked only once after initialization
        and push the k-value validation result.
        """
        start_thread = threading.Timer(
            5, self.push_dish_kvalue_validation_result
        )
        start_thread.start()

    def is_SetKValue_allowed(self) -> bool:
        """
        This method checks if the SetKValue Command is allowed in current
        State.
        :return: boolean value if command is allowed or not
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

        :param kvalue: k value between range 1-2222.
        :kvalue dtype: int
        :return: ResultCode and message
        :rtype: Tuple[List[ResultCode], List[str]]
        """
        if self.defective_params["enabled"]:
            return [ResultCode.FAILED], [
                self.defective_params["error_message"]
            ]
        self._kvalue = kvalue
        db = Database()
        value = {"kValue": {"__value": [self._kvalue]}}
        db.put_device_attribute_property(self._dishln_name, value)
        value = db.get_device_attribute_property(self._dishln_name, "kValue")
        self.logger.info("%s: memorized k-value %s", self._dishln_name, value)
        self._dish_kvalue_validation_result = str(int(ResultCode.OK))
        self.push_change_event(
            "kValueValidationResult", self._dish_kvalue_validation_result
        )
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

    def is_Off_allowed(self) -> bool:
        """
        This method checks if the Off Command is
        allowed in current
        State.
        :return: ``True`` if the command is allowed
        :rtype:bool
        :raises CommandNotAllowed: command is not allowed
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
        # Set the Dish Mode
        self.set_dish_mode(DishMode.STANDBY_LP)
        self.push_command_result(ResultCode.OK, "SetStandbyFPMode")
        self.logger.info("Off command completed.")
        return ([ResultCode.OK], [""])

    def is_SetStandbyFPMode_allowed(self) -> bool:
        """
        This method checks if the is_SetStandbyFPMode_allowed Command is
        allowed in current
        State.
        :return: ``True`` if the command is allowed
        :rtype:bool
        :raises CommandNotAllowed: command is not allowed
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
        :return: ResultCode and message
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
        self.logger.info("SetStandbyFPMode command completed.")
        return ([ResultCode.OK], [""])

    def is_SetStandbyLPMode_allowed(self) -> bool:
        """
        This method checks if the is_SetStandbyLPMode_allowed Command is
        allowed in current
        State.
        :return: ``True`` if the command is allowed
        :rtype: bool
        :raises CommandNotAllowed: command is not allowed
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
        :return: ResultCode and message
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

        # Set the Dish ModeLP
        self.set_dish_mode(DishMode.STANDBY_LP)
        self.push_command_result(ResultCode.OK, "SetStandbyLPMode")
        self.logger.info("SetStandbyLPMode command completed.")
        return ([ResultCode.OK], [""])

    def is_SetOperateMode_allowed(self) -> bool:
        """
        This method checks if the SetOperateMode Command is allowed in current
        State.
        :return: ``True`` if the command is allowed
        :rtype:bool
        :raises CommandNotAllowed: command is not allowed
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
        :return: ResultCode and message
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
        self.logger.info("SetOperateMode command completed.")
        return ([ResultCode.OK], [""])

    def is_SetStowMode_allowed(self) -> bool:
        """
        This method checks if the SetStowMode Command is allowed in current
        State.
        :return: ``True`` if the command is allowed
        :rtype: bool
        :raises CommandNotAllowed: command is not allowed
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
        :return: ResultCode and message
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
        self.logger.info("SetStowMode command completed.")
        return ([ResultCode.OK], [""])

    def is_Track_allowed(self) -> bool:
        """
        This method checks if the Track Command is allowed in current
        State.
        :return: ``True`` if the command is allowed
        :rtype: bool
        :raises CommandNotAllowed: command is not allowed
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
        :return: ResultCode and message
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
        self.logger.info("Track command completed.")
        return ([ResultCode.OK], [""])

    def is_TrackStop_allowed(self) -> bool:
        """
        This method checks if the TrackStop Command is allowed in current
        State.
        :return: ``True`` if the command is allowed
        :rtype: bool
        :raises CommandNotAllowed: command is not allowed
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
        :return: ResultCode and message
        :rtype: tuple
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
        achieved_pointing_thread = threading.Timer(
            interval=self._delay,
            function=self.set_achieved_pointing,
        )
        achieved_pointing_thread.start()

        self.push_command_result(ResultCode.OK, "TrackStop")
        self.logger.info("TrackStop command completed.")
        return ([ResultCode.OK], [""])

    def is_AbortCommands_allowed(self) -> bool:
        """
        This method checks if the AbortCommands command is allowed in current
        State.
        :return: ``True`` if the command is allowed
        :rtype: bool
        :raises CommandNotAllowed: command is not allowed
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
        :return: ResultCode and message
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
        :return: ``True`` if the command is allowed
        :rtype: bool
        :raises CommandNotAllowed: command is not allowed
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
        :return: ResultCode and message
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
        if self._pointing_state != PointingState.TRACK:
            if self._state_duration_info:
                self._follow_state_duration()
            else:
                self._pointing_state = PointingState.TRACK
                self.push_change_event("pointingState", self._pointing_state)
                self.logger.info("Pointing State: %s", self._pointing_state)

        # Set dish mode
        self.set_dish_mode(DishMode.OPERATE)

        thread = threading.Timer(
            self._delay,
            self.push_command_result,
            args=[ResultCode.OK, "Configure"],
            kwargs={"command_id": command_id},
        )
        thread.start()
        self.push_command_result(ResultCode.OK, "Configure")
        self.logger.info("Configure command completed.")
        return [ResultCode.QUEUED], [command_id]

    def is_TrackLoadStaticOff_allowed(self) -> bool:
        """
        This method checks if the TrackLoadStaticOff command is allowed in
        current State.
        :return: ``True`` if the command is allowed
        :rtype: bool
        :raises CommandNotAllowed: command is not allowed
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
        :return: ResultCode and message
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

    def is_Scan_allowed(self) -> Union[bool, CommandNotAllowed]:
        """
        This method checks if the Scan Command is allowed in current State.
        :return: ``True`` if the command is allowed
        :raises CommandNotAllowed: command is not allowed
        :rtype: Union[bool,CommandNotAllowed]
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
        dtype_in="DevString",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Scan(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes Scan command on Dish Master
        :param argin: scan_id as and string.
        :return: ResultCode and message
        :rtype: Tuple[List[ResultCode], List[str]]
        """
        self.logger.info("Processing Scan Command")
        # to record the command data
        self.update_command_info(SCAN, argin)
        if self.defective_params["enabled"]:
            return self.induce_fault("Scan")

            # TBD: Add your dish mode change logic here if required
        return ([ResultCode.OK], [""])

    def is_EndScan_allowed(self) -> Union[bool, CommandNotAllowed]:
        """
        This method checks if the EndScan Command is allowed in current State.
        :rtype:bool
        :raises CommandNotAllowed: command is not allowed
        :rtype: Union[bool,CommandNotAllowed]
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
        self.logger.info("EndScan Command is allowed")
        return True

    @command(
        dtype_in="DevVoid",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def EndScan(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method updates the scanID attribute of Dish Master
        :return: ResultCode and message
        :rtype: Tuple[List[ResultCode], List[str]]
        """
        # to record the command data
        self.update_command_info(END_SCAN)
        if self.defective_params["enabled"]:
            return self.induce_fault("EndScan")
            # On Real Dish Leaf Node the scanID attribute of Dish Master
            # is getting updated
            # TBD: Add your dish mode change logic here if required
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
