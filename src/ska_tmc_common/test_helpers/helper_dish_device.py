# pylint: disable=C0302
"""
This module implements the Helper Dish Device for testing an integrated TMC
"""
import json
import threading
import time
from typing import List, Tuple, Union

import numpy as np
import tango
from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from tango import AttrWriteType, DevState, DevString, EnsureOmniThread
from tango.server import attribute, command, run

from ska_tmc_common import CommandNotAllowed, FaultType
from ska_tmc_common.enum import Band, DishMode, PointingState
from ska_tmc_common.test_helpers.constants import (
    ABORT_COMMANDS,
    CONFIGURE_BAND_1,
    CONFIGURE_BAND_2,
    END_SCAN,
    SCAN,
    SET_OPERATE_MODE,
)
from ska_tmc_common.test_helpers.helper_dish_ln_device import (
    HelperDishLNDevice,
)


# pylint: disable=attribute-defined-outside-init,invalid-name
# pylint: disable=unused-argument,too-many-public-methods
class HelperDishDevice(HelperDishLNDevice):
    """A device exposing commands and attributes of the Dish device."""

    def init_device(self):
        super().init_device()
        self._pointing_state = PointingState.NONE
        self._configured_band = Band.NONE
        self._dish_mode = DishMode.STANDBY_LP
        self._achieved_pointing = [
            1707388147149.508,
            179.880204193508,
            31.877024524259,
        ]
        self._state_duration_info = []
        self._program_track_table = []
        self._program_track_table_lock = threading.Lock()
        self._scan_id = ""

    class InitCommand(SKABaseDevice.InitCommand):
        """A class for the HelperDishDevice's init_device() command."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            :return: ResultCode and message
            """
            super().do()
            self._device.set_change_event("configuredBand", True, False)
            self._device.set_change_event("achievedPointing", True, False)
            self._device.set_change_event("pointingState", True, False)
            self._device.set_change_event("dishMode", True, False)
            return (ResultCode.OK, "")

    pointingState = attribute(dtype=PointingState, access=AttrWriteType.READ)
    configuredBand = attribute(dtype=Band, access=AttrWriteType.READ)
    achievedPointing = attribute(
        dtype=(float,), access=AttrWriteType.READ, max_dim_x=3
    )
    dishMode = attribute(dtype=DishMode, access=AttrWriteType.READ)
    offset = attribute(dtype=str, access=AttrWriteType.READ)
    programTrackTable = attribute(
        dtype=(float,),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=150,
    )
    scanID = attribute(dtype=DevString, access=AttrWriteType.READ_WRITE)

    def read_scanID(self) -> str:
        """
        This method reads the scanID attribute of a dish.
        :rtype: str
        """
        return self._scan_id

    def write_scanID(self, value: str) -> None:
        """
        This method writes scanID attribute of dish.
        :param value: scan_id as given is the json
        :value dtype: str
        :rtype: None
        """
        self._scan_id = value

    @attribute(dtype=int, access=AttrWriteType.READ)
    def kValue(self) -> int:
        """
        This attribute is used for storing dish kvalue
        into tango DB.Made this attribute memorized so that when device
        restart then previous set kvalue will be used validation.
        :return: kValue
        """
        return self._kvalue

    def is_SetKValue_allowed(self) -> bool:
        """
        This method checks if the SetKValue Command is allowed in current
        State.
        :rtype: bool
        :return: boolean value if kValue is set or not
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
        :return: ResultCode and meeage
        :kvalue dtype: int
        :rtype: Tuple[List[ResultCode], List[str]]
        """
        if self.defective_params["enabled"]:
            return [ResultCode.FAILED], [
                self.defective_params["error_message"]
            ]
        self._kvalue = kvalue
        return ([ResultCode.OK], [""])

    def read_configuredBand(self) -> Band:
        """
        This method reads the configuredBand of dish.
        :return: configure band for dishes
        :rtype: Band
        """
        return self._configured_band

    def read_offset(self) -> str:
        """
        This method reads the offset of dishes.
        :return: offset for dishes
        :rtype: str
        """
        return json.dumps(self._offset)

    def read_programTrackTable(self) -> list:
        """
        This method reads the programTrackTable attribute of a dish.
        :return: programTrackTable for dishes
        :rtype: list
        """
        return self._program_track_table

    def write_programTrackTable(self, value: list) -> None:
        """
        This method writes the programTrackTable attribute of dish.
        :param value: 50 entries of timestamp, azimuth and elevation
        values of the desired pointing of dishes.
        Example: programTrackTable = [
        (timestamp1, azimuth1, elevation1),
        (timestamp2, azimuth2, elevation2),
        (timestamp3, azimuth3, elevation3),]
        :value dtype: list
        :rtype: None
        """
        with self._program_track_table_lock:
            self._program_track_table = value
            self.logger.info(
                "The programTrackTable attribute value: %s",
                self._program_track_table,
            )
            self.set_achieved_pointing()

    def read_achievedPointing(self) -> np.ndarray:
        """
        This method reads the achievedPointing of dishes.
        :return: achievedPointing of dishes
        :rtype: str
        """
        return np.array(self._achieved_pointing)

    @command(
        dtype_in=int,
        doc_in="Band to assign",
    )
    def SetDirectConfiguredBand(self, argin: Band) -> None:
        """
        Trigger a ConfiguredBand change
        """
        value = Band(argin)
        if self._configured_band != value:
            self._configured_band = Band(argin)
            self.push_change_event("configuredBand", self._configured_band)
            self.logger.info(
                "Dish configuredBand %s event is pushed", self._configured_band
            )

    @command(
        dtype_in=str,
        doc_in="Set Pointing State Duration",
    )
    def AddTransition(self, state_duration_info: str) -> None:
        """This command will set duration for pointing state such that when
        respective command for pointing state is triggered then it change
        pointing state after provided duration
        """
        self.logger.info(
            "Adding pointing state transitions for Dish device: %s",
            state_duration_info,
        )
        self._state_duration_info = json.loads(state_duration_info)

    @command(
        doc_in="Reset Pointing State Duration",
    )
    def ResetTransitions(self) -> None:
        """This command will reset PointingState duration which is set"""
        self.logger.info("Resetting Pointing State Duration")
        self._state_duration_info = []

    def set_configured_band(self, configured_band: Band) -> None:
        """
        This method set the Configured Band
        """
        self._configured_band = configured_band
        self.push_change_event("configuredBand", self._configured_band)
        self.logger.info("Configured Band: %s", self._configured_band)

    def update_command_info(
        self, command_name: str = "", command_input: str | bool | None = None
    ) -> None:
        """This method updates the commandCallInfo attribute,
        with the respective command information.

        Args:
            command_name (str): command name
            command_input(str or bool): Input argin for command
        """
        self.logger.info(
            "Recording the command data for DishMaster simulators"
        )

        self._command_info = (command_name, str(command_input))
        self._command_call_info.append(self._command_info)
        self.logger.info(
            "Recorded command_call_info list for DishMaster simulators \
            is %s",
            self._command_call_info,
        )
        self.push_change_event("commandCallInfo", self._command_call_info)
        self.logger.info("CommandCallInfo updates are pushed")

    def push_command_status(
        self,
        status,
        command_name: str,
        command_id=None,
    ) -> None:
        """Push long running command result event for given command.

        :params:

        result: The result code to be pushed as an event
        dtype: ResultCode

        command_name: The command name for which the event is being pushed
        dtype: str

        exception: Exception message to be pushed as an event
        dtype: str
        """
        if status == "COMPLETED":
            self.logger.info("Successfully processed %s command", command_name)
        elif status == "FAILED":
            self.logger.info(
                "Command %s failed, TaskStatus: %d", command_name, status
            )
        command_id = command_id or f"{time.time()}-{command_name}"
        command_status = (command_id, status)
        self.push_change_event("longRunningCommandStatus", command_status)

    def push_command_result(self, result_code, command_name):
        """Pushing a longRunningCommandResult event."""
        with EnsureOmniThread():
            command_id = f"1000_{command_name}"
            command_result = (
                command_id,
                str([result_code, f"{command_name} completed"]),
            )
            self.push_change_event("longRunningCommandResult", command_result)

    def set_achieved_pointing(self) -> None:
        """Sets the achieved pointing for dish."""
        try:
            self._achieved_pointing = self._program_track_table[0:3]
            self.logger.info(
                "The achieved pointing value is: %s",
                self._achieved_pointing,
            )
            self.push_change_event("achievedPointing", self._achieved_pointing)
        except (ValueError, TypeError, KeyError) as exp:
            self.logger.exception(
                "Exception occurred while pushing achieved pointing event: %s",
                exp,
            )

    def _update_poiniting_state_in_sequence(self) -> None:
        """This method update pointing state in sequence as per
        state duration info
        """
        for poiniting_state, duration in self._state_duration_info:
            pointing_state_enum = PointingState[poiniting_state]
            self.logger.info(
                "Sleep %s sec for pointing state %s",
                duration,
                poiniting_state,
            )
            time.sleep(duration)
            with tango.EnsureOmniThread():
                self.set_pointing_state(pointing_state_enum)

    def _follow_state_duration(self):
        """This method will update pointing state as per state duration"""
        thread = threading.Thread(
            target=self._update_poiniting_state_in_sequence,
        )
        thread.start()

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
        # Dish Mode Not Applicable.
        return ([ResultCode.OK], [""])

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
        dtype_in=("DevVarFloatArray"),
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def TrackLoadStaticOff(
        self, argin: List[float]
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes TrackLoadStaticOff command on Dish Master.

        :param argin: A list containing scan_id/ time, cross elevation and
            elevation offsets.
        :argin dtype: List(float)
        :return: ResultCode and message
        :rtype: Tuple[List[ResultCode], List[str]]
        """
        self.logger.info(
            "Instructed Dish simulator to invoke TrackLoadStaticOff command"
        )

        # Will be uncommented as a part of SAH-1530
        # command_id = f"{time.time()}-TrackLoadStaticOff"

        # Set offsets.
        cross_elevation = argin[0]
        elevation = argin[1]
        self.set_offset(cross_elevation, elevation)
        if self.defective_params[
            "enabled"
        ]:  # Temporary change to set status as failed.
            thread = threading.Timer(
                self._delay,
                function=self.push_command_result,
                args=["ResultCode.FAILED", "TrackLoadStaticOff"],
            )

            # Will be un-commented as part of SAH-1530
            #     kwargs={
            #         "command_id": command_id,
            #         "exception": "Failed to Load the static pointing "
            #         "model offsets",
            #     },
            # )
        else:
            thread = threading.Timer(
                self._delay,
                function=self.push_command_result,
                args=["ResultCode.OK", "TrackLoadStaticOff"],
            )
        thread.start()
        self.logger.info("Invocation of TrackLoadStaticOff command completed.")
        return ([ResultCode.QUEUED], [""])
        # will be un-commented as a part of SAH-1530
        # return ([ResultCode.QUEUED], [command_id])

    def is_ConfigureBand1_allowed(self) -> bool:
        """
        This method checks if the ConfigureBand1 command is allowed in current
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
        self.logger.info("ConfigureBand1 Command is allowed")
        return True

    @command(
        dtype_in=bool,
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ConfigureBand1(
        self, argin: bool
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes ConfigureBand1 command on Dish Master
        :param argin: The argin is a boolean value,
        if it is set true it invoke ConfigureBand1 command.
        :argin dtype: bool
        :return: ResultCode and message
        :rtype: tuple
        """
        self.logger.info("Processing ConfigureBand1 Command")
        # to record the command data
        self.update_command_info(CONFIGURE_BAND_1, argin)
        if self.defective_params["enabled"]:
            return self.induce_fault("ConfigureBand1")

        # Set the Dish Mode
        current_dish_mode = self._dish_mode
        self.set_dish_mode(DishMode.CONFIG)
        thread = threading.Thread(
            target=self.set_dish_mode,
            args=[current_dish_mode],
        )
        thread.start()
        # Set dish configured band
        self.set_configured_band(Band.B1)
        self.push_command_result(ResultCode.OK, "ConfigureBand1")
        self.logger.info("ConfigureBand1 command completed.")
        return ([ResultCode.OK], [""])

    def is_ConfigureBand2_allowed(self) -> bool:
        """
        This method checks if the ConfigureBand2 Command is allowed in current
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

        self.logger.info("ConfigureBand2 Command is allowed")
        return True

    @command(
        dtype_in=bool,
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ConfigureBand2(
        self, argin: bool
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes ConfigureBand2 command on Dish Master
        :param argin: The argin is a boolean value,
        if it is set true it invoke ConfigureBand2 command.
        :argin dtype: bool
        :return: ResultCode and message
        :rtype: tuple
        """
        self.logger.info("Current band - %s", self._configured_band)

        # Below changes will be un-commented in SAH-1530
        # if self._configured_band == Band.B2:
        #     self.push_command_result(
        #         ResultCode.REJECTED,
        #         "ConfigureBand2",
        #         exception="Already in band 2",
        #     )
        #     return ([ResultCode.REJECTED], ["Already in band 2"])

        # to record the command data
        self.update_command_info(CONFIGURE_BAND_2, argin)
        if self.defective_params["enabled"]:
            return self.induce_fault("ConfigureBand2")

        # Set the Dish Mode
        current_dish_mode = self._dish_mode
        self.set_dish_mode(DishMode.CONFIG)
        thread = threading.Thread(
            target=self.set_dish_mode,
            args=[current_dish_mode],
        )
        thread.start()
        # Set dish configured band
        self.set_configured_band(Band.B2)
        self.push_command_result(ResultCode.OK, "ConfigureBand2")
        self.logger.info("ConfigureBand2 command completed.")
        return ([ResultCode.OK], [""])

    def is_ConfigureBand3_allowed(self) -> bool:
        """
        This method checks if the ConfigureBand3 Command is allowed in current
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
        self.logger.info("ConfigureBand3 Command is allowed")
        return True

    @command(
        dtype_in=bool,
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ConfigureBand3(
        self, argin: bool
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes ConfigureBand3 command on  Dish Master
        :return: ResultCode and message
        """
        self.logger.info("Processing ConfigureBand3 Command")

        if self.defective_params["enabled"]:
            return self.induce_fault("ConfigureBand3")

        # Set dish mode
        self.set_dish_mode(DishMode.CONFIG)
        # Set dish configured band
        self.set_configured_band(Band.B3)
        self.push_command_result(ResultCode.OK, "ConfigureBand3")
        self.logger.info("ConfigureBand3 command completed.")
        return ([ResultCode.OK], [""])

    def is_ConfigureBand4_allowed(self) -> bool:
        """
        This method checks if the ConfigureBand4 Command is allowed in current
        State.
        :rtype: bool
        :return: ``True`` if the command is allowed
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
        self.logger.info("ConfigureBand4 Command is allowed")
        return True

    @command(
        dtype_in=bool,
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ConfigureBand4(
        self, argin: bool
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes ConfigureBand4 command on Dish Master
        :return: ResultCode and message
        """
        self.logger.info("Processing ConfigureBand4 Command")

        if self.defective_params["enabled"]:
            return self.induce_fault("ConfigureBand4")

        # Set dish mode
        self.set_dish_mode(DishMode.CONFIG)
        # Set dish configured band
        self.set_configured_band(Band.B4)
        self.push_command_result(ResultCode.OK, "ConfigureBand4")
        self.logger.info("ConfigureBand4 command completed.")
        return ([ResultCode.OK], [""])

    def is_ConfigureBand5a_allowed(self) -> bool:
        """
        This method checks if the ConfigureBand5a Command is allowed in current
        State.
        :rtype:bool
        :return: ``True`` if the command is allowed
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
        self.logger.info("ConfigureBand5a Command is allowed")
        return True

    @command(
        dtype_in=bool,
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ConfigureBand5a(
        self, argin: bool
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes ConfigureBand5a command on Dish Master
        :return: ResultCode and message
        """
        self.logger.info("Processing ConfigureBand5a Command")

        if self.defective_params["enabled"]:
            return self.induce_fault("ConfigureBand5a")
        # Set dish mode
        self.set_dish_mode(DishMode.CONFIG)
        # Set dish configured band
        self.set_configured_band(Band.B5a)
        self.push_command_result(ResultCode.OK, "ConfigureBand5a")
        self.logger.info("ConfigureBand5a command completed.")
        return ([ResultCode.OK], [""])

    def is_ConfigureBand5b_allowed(self) -> bool:
        """
        This method checks if the ConfigureBand5b Command is allowed in current
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
        self.logger.info("ConfigureBand5b Command is allowed")
        return True

    @command(
        dtype_in=bool,
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ConfigureBand5b(
        self, argin: bool
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes ConfigureBand5b command on Dish Master
        :return: ResultCode and message
        """
        self.logger.info("Processing ConfigureBand5b Command")

        if self.defective_params["enabled"]:
            return self.induce_fault("ConfigureBand5b")
        # Set dish mode
        self.set_dish_mode(DishMode.CONFIG)
        # Set dish configured band
        self.set_configured_band(Band.B5b)
        self.push_command_result(ResultCode.OK, "ConfigureBand5b")
        self.logger.info("ConfigureBand5b command completed.")
        return ([ResultCode.OK], [""])

    # def update_lrcr(
    #     self, command_name: str = "", command_id: str = ""
    # ) -> None:
    #     """Updates the longrunningcommandresult  after a delay."""
    #     delay_value = self._delay
    #     with tango.EnsureOmniThread():
    #         self.logger.info(
    #             "Sleep %s for command %s ", delay_value, command_name
    #         )
    #         time.sleep(delay_value)

    #         if self._pointing_state != PointingState.TRACK:
    #             if self._state_duration_info:
    #                 self._follow_state_duration()
    #             else:
    #                 self._pointing_state = PointingState.TRACK
    #                 self.push_change_event(
    #                     "pointingState", self._pointing_state
    #                 )

    #             # Set dish mode
    #         self.set_dish_mode(DishMode.OPERATE)
    #         self.push_command_result(
    #             ResultCode.OK, command_name, command_id=command_id
    #         )
    #         self.logger.info("Track command completed.")

    # Below changes will be un-commented in SAH-1530

    # @command(
    #     dtype_out="DevVarLongStringArray",
    #     doc_out="(ReturnType, 'informational message')",
    # )
    # def Track(self) -> Tuple[List[ResultCode], List[str]]:
    #     """
    #     This method invokes Track command on  Dish Master
    #     :return: ResultCode and message
    #     :rtype: tuple
    #     """
    #     command_id = f"{time.time()}-Track"
    #     self.logger.info("Instructed Dish simulator to invoke Track command")
    #     self.update_command_info(TRACK, "")
    #     if self.defective_params["enabled"]:
    #         return self.induce_fault("Track")

    #     thread = threading.Thread(
    #         target=self.update_lrcr, args=["Track", command_id]
    #     )
    #     thread.start()

    #     return ([ResultCode.QUEUED], [command_id])

    # TODO: Enable below commands when Dish Leaf Node implements them.
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
        :rtype: Union[bool,CommandNotAllowed]
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
        self.logger.info("Scan Command is allowed")
        return True

    @command(
        dtype_in="DevString",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Scan(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        This method sets scanID attribute of Dish Master.
        :return: Tuple[List[ResultCode], List[str]]
        """
        self.logger.info("Processing Scan Command")
        # to record the command data
        self.update_command_info(SCAN, argin)
        if self.defective_params["enabled"]:
            return self.induce_fault("Scan")
        self._scan_id = argin
        self.push_command_status("COMPLETED", "Scan")
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
        This method clears the scanID attribute of Dish Master
        :return: ResultCode and message
        :rtype: Tuple[List[ResultCode], List[str]]
        """
        # to record the command data
        self.update_command_info(END_SCAN)
        if self.defective_params["enabled"]:
            return self.induce_fault("EndScan")
        self._scan_id = ""
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
    return run((HelperDishDevice,), args=args, **kwargs)


if __name__ == "__main__":
    main()
