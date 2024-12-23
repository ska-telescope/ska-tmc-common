# pylint: disable=C0302
"""
This module implements the Helper Dish Device for testing an integrated TMC
"""
import json
import threading
import time
from datetime import datetime
from typing import List, Tuple, Union

import numpy as np
import tango
from astropy.time import Time
from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from tango import AttrWriteType, DevFloat, DevState, DevString
from tango.server import attribute, command, run

from ska_tmc_common import CommandNotAllowed, FaultType
from ska_tmc_common.enum import (
    Band,
    DishMode,
    PointingState,
    TrackTableLoadMode,
)
from ska_tmc_common.exceptions import CoefficientError
from ska_tmc_common.test_helpers.constants import (
    ABORT_COMMANDS,
    CONFIGURE_BAND_1,
    CONFIGURE_BAND_2,
    END_SCAN,
    SCAN,
    SET_OPERATE_MODE,
    SKA_EPOCH,
    TRACK,
    TRACK_STOP,
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
        self._configured_band = Band.NONE
        self._achieved_pointing = [
            (
                Time(datetime.today(), scale="utc").unix_tai
                - Time(SKA_EPOCH, scale="utc").unix_tai
            ),
            179.880204193508,
            31.877024524259,
        ]
        self._state_duration_info: dict = {}
        self._program_track_table = np.array([])
        self._program_track_table_lock = threading.Lock()
        self._scan_id = ""
        self._global_pointing_data: str = ""
        self._track_table_load_mode: TrackTableLoadMode = (
            TrackTableLoadMode.APPEND
        )
        self._band1PointingModelParams = []
        self._band2PointingModelParams = []
        self._band3PointingModelParams = []
        self._band4PointingModelParams = []
        self._band5aPointingModelParams = []
        self._band5bPointingModelParams = []
        self.thread = None
        self.track_stop = False

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
            self._device.set_change_event("scanID", True, False)
            self._device.set_change_event("TrackTableLoadMode", True, False)
            self._device.set_change_event(
                "band1PointingModelParams", True, False
            )
            self._device.set_change_event(
                "band2PointingModelParams", True, False
            )
            self._device.set_change_event(
                "band3PointingModelParams", True, False
            )
            self._device.set_change_event(
                "band4PointingModelParams", True, False
            )
            self._device.set_change_event(
                "band5APointingModelParams", True, False
            )
            self._device.set_change_event(
                "band5BPointingModelParams", True, False
            )

            return (ResultCode.OK, "")

    configuredBand = attribute(dtype=Band, access=AttrWriteType.READ)
    achievedPointing = attribute(
        dtype=(float,), access=AttrWriteType.READ, max_dim_x=3
    )
    offset = attribute(dtype=str, access=AttrWriteType.READ)
    programTrackTable = attribute(
        dtype=(float,),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=150,
    )
    scanID = attribute(dtype=DevString, access=AttrWriteType.READ_WRITE)
    band1PointingModelParams = attribute(
        dtype=(DevFloat,), access=AttrWriteType.READ_WRITE, max_dim_x=18
    )
    band2PointingModelParams = attribute(
        dtype=(DevFloat,), access=AttrWriteType.READ_WRITE, max_dim_x=18
    )
    band3PointingModelParams = attribute(
        dtype=(DevFloat,), access=AttrWriteType.READ_WRITE, max_dim_x=18
    )
    band4PointingModelParams = attribute(
        dtype=(DevFloat,), access=AttrWriteType.READ_WRITE, max_dim_x=18
    )
    band5aPointingModelParams = attribute(
        dtype=(DevFloat,), access=AttrWriteType.READ_WRITE, max_dim_x=18
    )
    band5bPointingModelParams = attribute(
        dtype=(DevFloat,), access=AttrWriteType.READ_WRITE, max_dim_x=18
    )

    def read_band1PointingModelParams(self) -> List[float]:
        """
        This method reads the band1PointingModelParams attribute of a dish.
        :rtype: List
        """
        return self._band1PointingModelParams

    def write_band1PointingModelParams(self, value):
        """
        This method writes band1PointingModelParams attribute of dish.
        :param value: _band1PointingModelParams as given is the json
        :value dtype: List
        :rtype: None
        """
        self._band1PointingModelParams = value

    def read_band2PointingModelParams(self) -> List[float]:
        """
        This method reads the band2PointingModelParams attribute of a dish.
        :rtype: List
        """
        return self._band2PointingModelParams

    def write_band2PointingModelParams(self, value):
        """
        This method writes band2PointingModelParams attribute of dish.
        :param value: _band2PointingModelParams as given is the json
        :value dtype: List
        :rtype: None
        """
        self._band2PointingModelParams = value

    def read_band3PointingModelParams(self) -> List[float]:
        """
        This method reads the band3PointingModelParams attribute of a dish.
        :rtype: List
        """
        return self._band3PointingModelParams

    def write_band3PointingModelParams(self, value):
        """
        This method writes band3PointingModelParams attribute of dish.
        :param value: _band3PointingModelParams as given is the json
        :value dtype: List
        :rtype: None
        """
        self._band3PointingModelParams = value

    def read_band4PointingModelParams(self) -> List[float]:
        """
        This method reads the band4PointingModelParams attribute of a dish.
        :rtype: List
        """
        return self._band4PointingModelParams

    def write_band4PointingModelParams(self, value):
        """
        This method writes band4PointingModelParams attribute of dish.
        :param value: _band4PointingModelParams as given is the json
        :value dtype: List
        :rtype: None
        """
        self._band4PointingModelParams = value

    def read_band5aPointingModelParams(self) -> List[float]:
        """
        This method reads the band5aPointingModelParams attribute of a dish.
        :rtype: List
        """
        return self._band5aPointingModelParams

    def write_band5aPointingModelParams(self, value):
        """
        This method writes band5aPointingModelParams attribute of dish.
        :param value: _band5aPointingModelParams as given is the json
        :value dtype: List
        :rtype: None
        """
        self._band5aPointingModelParams = value

    def read_band5bPointingModelParams(self) -> List[float]:
        """
        This method reads the band5bPointingModelParams attribute of a dish.
        :rtype: List
        """
        return self._band5bPointingModelParams

    def write_band5bPointingModelParams(self, value):
        """
        This method writes band5bPointingModelParams attribute of dish.
        :param value: _band5bPointingModelParams as given is the json
        :value dtype: List
        :rtype: None
        """
        self._band5bPointingModelParams = value

    @property
    def configured_band(self):
        """Gets the currently configured band.
            This property returns the band that has been configured for
            instance.
        Returns:
            Band: The currently configured band."""
        return self._configured_band

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

    @attribute(
        dtype=TrackTableLoadMode,
        access=AttrWriteType.READ_WRITE,
        doc="Selects track table load mode.\nWith APPEND selected, Dish will "
        "add the coordinate set given in programTrackTable attribute to the "
        "list of pointing coordinates already loaded in ACU.\nWith NEW "
        "selected, Dish will delete the list of pointing coordinates "
        "previously loaded in ACU when new coordinates are given in the "
        "programTrackTable attribute.",
    )
    def trackTableLoadMode(self) -> TrackTableLoadMode:
        """
        Returns the trackTableLoadMode.
        :rtype: TrackTableLoadMode
        """
        return self._track_table_load_mode

    @trackTableLoadMode.write
    def trackTableLoadMode(self, value: TrackTableLoadMode) -> None:
        """
        Set the trackTableLoadMode.
        :param value: TrackTableLoadMode (NEW or APPEND)
        :value dtype: TrackTableLoadMode
        :rtype: None
        """
        self._track_table_load_mode = value
        self.push_change_event("trackTableLoadMode", value)
        self.push_archive_event("trackTableLoadMode", value)
        if self._track_table_load_mode == TrackTableLoadMode.NEW:
            with self._program_track_table_lock:
                self._program_track_table = np.array([])

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
        return self.configured_band

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
        if self.configured_band != value:
            self._configured_band = Band(argin)
            self.push_change_event("configuredBand", self.configured_band)
            self.logger.info(
                "Dish configuredBand %s event is pushed", self.configured_band
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
        self._state_duration_info = {}

    def set_configured_band(self, configured_band: Band) -> None:
        """
        This method set the Configured Band
        """
        self._configured_band = configured_band
        self.push_change_event("configuredBand", self.configured_band)
        self.logger.info("Configured Band: %s", self.configured_band)

    def update_command_info(
        self, command_name: str = "", command_input: str | bool | None = None
    ) -> None:
        """This method updates the commandCallInfo attribute,
        with the respective command information.

        Args:
            command_name (str): command name
            command_input(str or bool): Input argin for command
        """
        self._command_info = (command_name, str(command_input))
        self._command_call_info.append(self._command_info)
        self.logger.info(
            "Recorded command_call_info list for %s is %s",
            self.dev_name,
            self._command_call_info,
        )
        self.push_change_event("commandCallInfo", self._command_call_info)
        self.logger.info("CommandCallInfo updates are pushed")

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
        command_id = f"{time.time()}_SetOperateMode"
        self.logger.info(
            "Instructed Dish simulator to invoke SetOperateMode command"
        )
        self.update_command_info(SET_OPERATE_MODE, "")
        if self.defective_params["enabled"]:
            return self.induce_fault(
                "SetOperateMode", command_id, is_dish=True
            )

        # Set the device state
        if self.dev_state() != DevState.ON:
            self.set_state(DevState.ON)
            self.push_change_event("State", self.dev_state())
        # Set the pointing state
        # if self._pointing_state != PointingState.READY:
        #     self._pointing_state = PointingState.READY
        #     self.push_change_event("pointingState", self._pointing_state)

        # Set the Dish Mode
        self.set_dish_mode(DishMode.OPERATE)
        self.push_command_result(
            ResultCode.OK, "SetOperateMode", command_id=command_id
        )
        self.logger.info("SetOperateMode command completed.")
        return (
            [ResultCode.QUEUED],
            [command_id],
        )

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
        command_id = f"{time.time()}_AbortCommands"
        self.logger.info(
            "Instructed Dish simulator to invoke AbortCommands command"
        )
        self.update_command_info(ABORT_COMMANDS, "")

        if self.defective_params["enabled"]:
            return self.induce_fault("AbortCommands", command_id, is_dish=True)

        self._pointing_state = PointingState.READY
        self.push_change_event("pointingState", self._pointing_state)
        # Set the Dish Mode
        self.set_dish_mode(DishMode.STANDBY_FP)
        self.logger.info("AbortCommands Completed")
        return (
            [ResultCode.OK],
            [command_id],
        )

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
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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
        self.update_command_info("TrackLoadStaticOff", str(argin))

        # Will be uncommented as a part of SAH-1530
        command_id = f"{time.time()}-TrackLoadStaticOff"

        # Set offsets.
        cross_elevation = argin[0]
        elevation = argin[1]
        self.set_offset(cross_elevation, elevation)
        if self.defective_params[
            "enabled"
        ]:  # Temporary change to set status as failed.
            return self.induce_fault(
                "TrackLoadStaticOff", command_id, is_dish=True
            )
        thread = threading.Timer(
            self._delay,
            function=self.push_command_result,
            args=[ResultCode.OK, "TrackLoadStaticOff"],
            kwargs={"command_id": command_id},
        )
        thread.start()
        self.logger.info("Invocation of TrackLoadStaticOff command completed.")
        return [ResultCode.QUEUED], [command_id]

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
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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
        command_id = f"{time.time()}_ConfigureBand1"
        self.logger.info("Processing ConfigureBand1 Command")
        # to record the command data
        self.update_command_info(CONFIGURE_BAND_1, argin)
        if self.defective_params["enabled"]:
            return self.induce_fault(
                "ConfigureBand1", command_id, is_dish=True
            )

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
        self.push_command_result(
            ResultCode.OK, "ConfigureBand1", command_id=command_id
        )
        self.logger.info("ConfigureBand1 command completed.")
        return [ResultCode.QUEUED], [command_id]

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
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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
        command_id = f"{time.time()}_ConfigureBand2"
        self.logger.info("Current band - %s", self.configured_band)

        # TODO: The scenario of duplicate band is under discussion. Need to
        # enable below statements once the behaviour is fixed.
        # if self.configured_band == Band.B2:
        #     self.push_command_result(
        #         ResultCode.REJECTED,
        #         "ConfigureBand2",
        #         message="Dish is already configured for BAND2 ",
        #     )
        #     return (
        #         [ResultCode.REJECTED],
        #         ["Dish is already configured for BAND2 "],
        #     )

        # to record the command data
        self.update_command_info(CONFIGURE_BAND_2, argin)
        if self.defective_params["enabled"]:
            return self.induce_fault(
                "ConfigureBand2", command_id, is_dish=True
            )

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
        self.push_command_result(
            ResultCode.OK, "ConfigureBand2", command_id=command_id
        )
        self.logger.info("ConfigureBand2 command completed.")
        return [ResultCode.QUEUED], [command_id]

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
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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
        command_id = f"{time.time()}_ConfigureBand3"

        self.logger.info("Processing ConfigureBand3 Command")

        if self.defective_params["enabled"]:
            return self.induce_fault(
                "ConfigureBand3", command_id, is_dish=True
            )

        # Set dish mode
        current_dish_mode = self._dish_mode
        self.set_dish_mode(DishMode.CONFIG)
        thread = threading.Thread(
            target=self.set_dish_mode,
            args=[current_dish_mode],
        )
        thread.start()
        # Set dish configured band
        self.set_configured_band(Band.B3)
        self.push_command_result(
            ResultCode.OK, "ConfigureBand3", command_id=command_id
        )
        self.logger.info("ConfigureBand3 command completed.")
        return [ResultCode.QUEUED], [command_id]

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
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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
        command_id = f"{time.time()}_ConfigureBand4"
        self.logger.info("Processing ConfigureBand4 Command")

        if self.defective_params["enabled"]:
            return self.induce_fault(
                "ConfigureBand4", command_id, is_dish=True
            )

        # Set dish mode
        current_dish_mode = self._dish_mode
        self.set_dish_mode(DishMode.CONFIG)
        thread = threading.Thread(
            target=self.set_dish_mode,
            args=[current_dish_mode],
        )
        thread.start()
        # Set dish configured band
        self.set_configured_band(Band.B4)
        self.push_command_result(
            ResultCode.OK, "ConfigureBand4", command_id=command_id
        )
        self.logger.info("ConfigureBand4 command completed.")
        return [ResultCode.QUEUED], [command_id]

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
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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
        command_id = f"{time.time()}_ConfigureBand5a"
        self.logger.info("Processing ConfigureBand5a Command")

        if self.defective_params["enabled"]:
            return self.induce_fault(
                "ConfigureBand5a", command_id, is_dish=True
            )
        # Set dish mode
        current_dish_mode = self._dish_mode
        self.set_dish_mode(DishMode.CONFIG)
        thread = threading.Thread(
            target=self.set_dish_mode,
            args=[current_dish_mode],
        )
        thread.start()
        # Set dish configured band
        self.set_configured_band(Band.B5a)
        self.push_command_result(
            ResultCode.OK, "ConfigureBand5a", command_id=command_id
        )
        self.logger.info("ConfigureBand5a command completed.")
        return [ResultCode.QUEUED], [command_id]

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
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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
        command_id = f"{time.time()}_ConfigureBand5b"

        self.logger.info("Processing ConfigureBand5b Command")

        if self.defective_params["enabled"]:
            return self.induce_fault(
                "ConfigureBand5b", command_id, is_dish=True
            )
        # Set dish mode
        current_dish_mode = self._dish_mode
        self.set_dish_mode(DishMode.CONFIG)
        thread = threading.Thread(
            target=self.set_dish_mode,
            args=[current_dish_mode],
        )
        thread.start()
        # Set dish configured band
        self.set_configured_band(Band.B5b)
        self.push_command_result(
            ResultCode.OK, "ConfigureBand5b", command_id=command_id
        )
        self.logger.info("ConfigureBand5b command completed.")
        return [ResultCode.QUEUED], [command_id]

    # Below changes will be un-commented in SAH-1530

    def update_lrcr(
        self, command_name: str = "", command_id: str = ""
    ) -> None:
        """Updates the longrunningcommandresult  after a delay."""
        delay_value = self._delay
        with tango.EnsureOmniThread():
            time.sleep(delay_value)
            if not self.track_stop:
                if self._pointing_state != PointingState.TRACK:
                    if self._state_duration_info:
                        self._follow_state_duration()
                    else:
                        self._pointing_state = PointingState.TRACK
                        self.push_change_event(
                            "pointingState", self._pointing_state
                        )

                    # Set dish mode
                self.set_dish_mode(DishMode.OPERATE)
                self.push_command_result(
                    ResultCode.OK, command_name, command_id=command_id
                )
                self.logger.info("%s command completed.", command_name)

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
        command_id = f"{time.time()}-Track"
        self.logger.info("Instructed Dish simulator to invoke Track command")
        self.update_command_info(TRACK, "")
        if self.defective_params["enabled"]:
            return self.induce_fault("Track", command_id, is_dish=True)

        self.thread = threading.Thread(
            target=self.update_lrcr, args=["Track", command_id]
        )
        self.thread.start()
        return ([ResultCode.QUEUED], [command_id])

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
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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
        command_id = f"{time.time()}_Scan"
        self.logger.info("Processing Scan Command")
        # to record the command data
        self.update_command_info(SCAN, argin)
        if self.defective_params["enabled"]:
            return self.induce_fault("Scan", command_id, is_dish=True)
        self._scan_id = argin
        self.push_command_result(ResultCode.OK, "Scan", command_id=command_id)
        return [ResultCode.QUEUED], [command_id]

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
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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
        command_id = f"{time.time()}_EndScan"
        # to record the command data
        self.update_command_info(END_SCAN)
        if self.defective_params["enabled"]:
            return self.induce_fault("EndScan", command_id, is_dish=True)
        self._scan_id = ""
        self.push_command_result(
            ResultCode.OK, "EndScan", command_id=command_id
        )
        return (
            [ResultCode.QUEUED],
            [command_id],
        )

    def process_json_to_band_params(self, json_data: str) -> None:
        """
        Processes the given JSON string, extracts 'coefficients'
        values in a specified order,
        and assigns them to an attribute based on the 'band' value.
        :raises CoefficientError: Not implemented error
        """
        # Load JSON data
        data = json.loads(json_data)

        # Define expected keys in the required order
        required_keys = [
            "IA",
            "CA",
            "NPAE",
            "AN",
            "AN0",
            "AW",
            "AW0",
            "ACEC",
            "ACES",
            "ABA",
            "ABphi",
            "IE",
            "ECEC",
            "ECES",
            "HECE4",
            "HESE4",
            "HECE8",
            "HESE8",
        ]

        # Check if all required coefficients are present
        coefficients = data.get("coefficients", {})
        missing_keys = [
            key for key in required_keys if key not in coefficients
        ]
        if missing_keys:
            raise CoefficientError(
                f"Missing coefficient values for: {', '.join(missing_keys)}"
            )

        # Extract values in the specified order
        values_list = [coefficients[key]["value"] for key in required_keys]

        # Determine which attribute to set based on 'band' value
        bandPointingModelParams = (
            f"band{data.get('band').split('_')[1]}PointingModelParams"
        )
        setattr(self, f"_{bandPointingModelParams}", values_list)
        self.push_change_event(bandPointingModelParams, values_list)
        self.push_archive_event(bandPointingModelParams, values_list)

    @command(dtype_in="str", dtype_out="DevVarLongStringArray")
    def ApplyPointingModel(
        self, global_pointing_data: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This method applies the received global pointing model data.
        Its a dummy command at present.
        Will be renamed, once Dish ICD gets updated.

        :param global_pointing_data: Global pointing data
        :type global_pointing_data: str
        :return: ResultCode and message
        :rtype: Tuple[List[ResultCode], List[str]]
        """
        try:
            self.process_json_to_band_params(global_pointing_data)
        except CoefficientError as e:
            # Log the error and return a failure result code and message
            self.logger.exception("CoefficientError: %s", e)
            return [ResultCode.FAILED], [f"ApplyPointingModel failed:{str(e)}"]

        command_id = f"{time.time()}_ApplyPointingModel"
        try:
            if self.defective_params[
                "enabled"
            ]:  # Temporary change to set status as failed.
                thread = threading.Timer(
                    self._delay,
                    function=self.push_command_result,
                    args=[ResultCode.FAILED, "ApplyPointingModel"],
                    kwargs={
                        "message": "Failed to execute ApplyPointingModel",
                        "command_id": command_id,
                    },
                )
            else:
                thread = threading.Timer(
                    self._delay,
                    function=self.push_command_result,
                    args=[ResultCode.OK, "ApplyPointingModel"],
                    kwargs={"command_id": command_id},
                )
            thread.start()
            self._global_pointing_data = json.loads(global_pointing_data)
            self.logger.info(
                "Processed Global pointing data successfully. Data is: %s",
                self._global_pointing_data,
            )
            return [ResultCode.OK], [command_id]
        except json.JSONDecodeError as e:
            self.logger.exception("Failed to decode JSON: %s", e)
            return [ResultCode.FAILED], ["Failed to decode JSON"]

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
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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
        command_id = f"{time.time()}_TrackStop"
        self.logger.info(
            "Instructed Dish simulator to invoke TrackStop command"
        )
        self.update_command_info(TRACK_STOP, "")
        self.track_stop = True
        if self.defective_params["enabled"]:
            return self.induce_fault("TrackStop", command_id, is_dish=True)
        if self._pointing_state != PointingState.READY:
            if self._state_duration_info:
                self._follow_state_duration()
            else:
                self._pointing_state = PointingState.READY
                self.push_change_event("pointingState", self._pointing_state)
                self.logger.info("Pointing State: %s", self._pointing_state)
        # Set dish mode
        self.set_dish_mode(DishMode.OPERATE)
        self.push_command_result(
            ResultCode.OK, "TrackStop", command_id=command_id
        )
        self.track_stop = False
        self.logger.info("TrackStop command completed.")
        return [ResultCode.QUEUED], [command_id]


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
