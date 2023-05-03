import threading
import time
from typing import Literal

from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from tango import AttrWriteType, DevEnum, DevState
from tango.server import attribute, command

from ska_tmc_common.enum import DishMode, PointingState
from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice


class HelperDishDevice(HelperBaseDevice):
    """A device exposing commands and attributes of the Dish device."""

    def init_device(self):
        super().init_device()
        self._pointing_state = PointingState.NONE
        self._dish_mode = DishMode.STANDBY_LP

    class InitCommand(SKABaseDevice.InitCommand):
        def do(self):
            super().do()
            self._device.set_change_event("pointingState", True, False)
            self._device.set_change_event("dishMode", True, False)
            return (ResultCode.OK, "")

    pointingState = attribute(dtype=PointingState, access=AttrWriteType.READ)
    dishMode = attribute(dtype=DishMode, access=AttrWriteType.READ)

    def read_pointingState(self) -> PointingState:
        return self._pointing_state

    def read_dishMode(self) -> DishMode:
        return self._dish_mode

    @command(
        dtype_in=DevEnum,
        doc_in="Assign Dish Mode.",
    )
    def SetDirectDishMode(self, argin) -> None:
        """
        Trigger a DishMode change
        """
        if not self._defective:
            self.set_dish_mode(argin)

    @command(
        dtype_in=int,
        doc_in="pointing state to assign",
    )
    def SetDirectPointingState(self, argin) -> None:
        """
        Trigger a PointingState change
        """
        # import debugpy; debugpy.debug_this_thread()
        if not self._defective:
            value = PointingState(argin)
            if self._pointing_state != value:
                self._pointing_state = PointingState(argin)
                self.push_change_event("pointingState", self._pointing_state)

    def set_dish_mode(self, dishMode) -> None:
        if not self._defective:
            if self._dish_mode != dishMode:
                self._dish_mode = dishMode
                time.sleep(0.1)
                self.push_change_event("dishMode", self._dish_mode)

    def is_Standby_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Standby(self):
        # Set the device state
        if not self._defective:
            if self.dev_state() != DevState.STANDBY:
                self.set_state(DevState.STANDBY)
                time.sleep(0.1)
                self.push_change_event("State", self.dev_state())
            # Set the Dish Mode
            self.set_dish_mode(DishMode.STANDBY_LP)
            return ([ResultCode.OK], [""])
        else:
            return [ResultCode.FAILED], [
                "Device is Defective, cannot process command."
            ]

    def is_SetStandbyFPMode_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetStandbyFPMode(self):
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
        else:
            return [ResultCode.FAILED], [
                "Device is Defective, cannot process command."
            ]

    def is_SetStandbyLPMode_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetStandbyLPMode(self):
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
        else:
            return [ResultCode.FAILED], [
                "Device is Defective, cannot process command."
            ]

    def is_SetOperateMode_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetOperateMode(self):
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
        else:
            return [ResultCode.FAILED], [
                "Device is Defective, cannot process command."
            ]

    def is_SetStowMode_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetStowMode(self):
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
        else:
            return [ResultCode.FAILED], [
                "Device is Defective, cannot process command."
            ]

    def is_Track_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Track(self):
        if not self._defective:
            self.logger.info("Processing Track Command")
            if self._pointing_state != PointingState.TRACK:
                self._pointing_state = PointingState.TRACK
                self.push_change_event("pointingState", self._pointing_state)
            # Set dish mode
            self.set_dish_mode(DishMode.OPERATE)
            return ([ResultCode.OK], [""])
        else:
            return [ResultCode.FAILED], [
                "Device is Defective, cannot process command."
            ]

    def is_TrackStop_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_in="DevVoid",
        doc_out="(ReturnType, 'DevVoid')",
    )
    def TrackStop(self):
        if not self._defective:
            self.logger.info("Processing TrackStop Command")
            if self._pointing_state != PointingState.READY:
                self._pointing_state = PointingState.READY
                self.push_change_event("pointingState", self._pointing_state)
                self.logger.info(f"Pointing State: {self._pointing_state}")
            # Set dish mode
            self.set_dish_mode(DishMode.OPERATE)

    def is_AbortCommands_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def AbortCommands(self):
        self.logger.info("Abort Completed")
        # Dish Mode Not Applicable.
        return ([ResultCode.OK], [""])

    def is_Configure_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_in=("DevString"),
        doc_out="(ReturnType, 'DevVarLongStringArray')",
    )
    def Configure(self, argin):
        if not self._defective:
            self.logger.info("Processing Configure command")
            return [ResultCode.OK], ["Configure completed"]
        return [ResultCode.FAILED], ["Device defective. Configure Failed."]

    def is_ConfigureBand1_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_in=("DevString"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def ConfigureBand1(self, argin):
        if not self._defective:
            self.logger.info("Processing ConfigureBand1")
            # Set dish mode
            self.set_dish_mode(DishMode.CONFIG)

    def is_ConfigureBand2_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_in=("DevString"),
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'DevVarLongStringArray')",
    )
    def ConfigureBand2(self, argin):
        current_dish_mode = self._dish_mode
        if not self._defective:
            self.logger.info("Processing ConfigureBand2")
            # Create thread which update dishMode
            start_dish_mode_transition = threading.Thread(
                None,
                self.start_config_transition,
                "DishHelper",
                args=(current_dish_mode,),
            )
            start_dish_mode_transition.start()
            return ([ResultCode.OK], [""])
        else:
            return [ResultCode.FAILED], [
                "Device is Defective, cannot process command."
            ]

    def start_config_transition(self, current_dish_mode: DishMode) -> None:
        """Update Dish Mode to CONFIG and then to current_dish_mode"""
        self.set_dish_mode(DishMode.CONFIG)
        time.sleep(2)
        self.set_dish_mode(current_dish_mode)

    def is_ConfigureBand3_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_in=("DevString"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def ConfigureBand3(self, argin):
        if not self._defective:
            self.logger.info("Processing ConfigureBand3")
            # Set dish mode
            self.set_dish_mode(DishMode.CONFIG)

    def is_ConfigureBand4_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_in=("DevString"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def ConfigureBand4(self, argin):
        if not self._defective:
            self.logger.info("Processing ConfigureBand4")
            # Set dish mode
            self.set_dish_mode(DishMode.CONFIG)

    def is_ConfigureBand5a_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_in=("DevString"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def ConfigureBand5a(self, argin):
        if not self._defective:
            self.logger.info("Processing ConfigureBand5a")
            # Set dish mode
            self.set_dish_mode(DishMode.CONFIG)

    def is_ConfigureBand5b_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_in=("DevString"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def ConfigureBand5b(self, argin):
        if not self._defective:
            self.logger.info("Processing ConfigureBand5")
            # Set dish mode
            self.set_dish_mode(DishMode.CONFIG)

    def is_Slew_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_in=("DevVarDoubleArray"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def Slew(self):
        if not self._defective:
            if self._pointing_state != PointingState.SLEW:
                self._pointing_state = PointingState.SLEW
                self.push_change_event("pointingState", self._pointing_state)
            # TBD: Dish mode change

    @command(
        dtype_in=("DevVoid"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def StartCapture(self):
        # TBD: Dish mode change
        pass

    @command(
        dtype_in=("DevVoid"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def SetMaintenanceMode(self):
        # TBD: Dish mode change
        pass

    def is_Scan_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_in=("DevVoid"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def Scan(self):
        # TBD: Dish mode change
        self.logger.info("Processing Scan")

    def is_Reset_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_in=("DevVoid"),
        doc_out="(ReturnType, 'informational message')",
    )
    def Reset(self):
        # TBD: Dish mode change
        return ([ResultCode.OK], [""])
