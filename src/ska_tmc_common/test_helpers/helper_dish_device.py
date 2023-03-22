import time

from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import HealthState
from tango import AttrWriteType, DevEnum, DevState
from tango.server import attribute, command

from ska_tmc_common.enum import DishMode, PointingState
from ska_tmc_common.test_helpers.helper_csp_master_device import (
    EmptyComponentManager,
)


class HelperDishDevice(SKABaseDevice):
    """A device exposing commands and attributes of the Dish device."""

    def init_device(self):
        super().init_device()
        self._health_state = HealthState.OK
        self._pointing_state = PointingState.NONE
        self._dish_mode = DishMode.UNKNOWN

    class InitCommand(SKABaseDevice.InitCommand):
        def do(self):
            super().do()
            self._device.set_change_event("State", True, False)
            self._device.set_change_event("healthState", True, False)
            self._device.set_change_event("pointingState", True, False)
            self._device.set_change_event("dishMode", True, False)
            return (ResultCode.OK, "")

    pointingState = attribute(dtype=PointingState, access=AttrWriteType.READ)
    dishMode = attribute(dtype=DishMode, access=AttrWriteType.READ)

    def read_pointingState(self):
        return self._pointing_state

    def read_dishMode(self):
        return self._dish_mode

    def create_component_manager(self):
        cm = EmptyComponentManager(
            logger=self.logger,
            max_workers=None,
            communication_state_callback=None,
            component_state_callback=None,
        )
        return cm

    def always_executed_hook(self):
        pass

    def delete_device(self):
        pass

    @command(
        dtype_in="DevState",
        doc_in="state to assign",
    )
    def SetDirectState(self, argin):
        """
        Trigger a DevState change
        """
        # import debugpy; debugpy.debug_this_thread()
        if self.dev_state() != argin:
            self.set_state(argin)
            time.sleep(0.1)
            self.push_change_event("State", self.dev_state())

    @command(
        dtype_in=int,
        doc_in="health state to assign",
    )
    def SetDirectHealthState(self, argin):
        """
        Trigger a HealthState change
        """
        # import debugpy; debugpy.debug_this_thread()
        value = HealthState(argin)
        if self._health_state != value:
            self._health_state = HealthState(argin)
            self.push_change_event("healthState", self._health_state)

    @command(
        dtype_in=DevEnum,
        doc_in=" Assign Dish Mode.",
    )
    def SetDirectDishMode(self, argin):
        """
        Trigger a DishMode change
        """
        self.set_dish_mode(argin)

    @command(
        dtype_in=int,
        doc_in="pointing state to assign",
    )
    def SetDirectPointingState(self, argin):
        """
        Trigger a PointingState change
        """
        # import debugpy; debugpy.debug_this_thread()
        value = PointingState(argin)
        if self._pointing_state != value:
            self._pointing_state = PointingState(argin)
            self.push_change_event("pointingState", self._pointing_state)

    def set_dish_mode(self, dishMode):
        if self._dish_mode != dishMode:
            self._dish_mode = dishMode
            time.sleep(0.1)
            self.push_change_event("dishMode", self._dish_mode)

    def is_On_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def On(self):
        # Set device state
        if self.dev_state() != DevState.ON:
            self.set_state(DevState.ON)
            time.sleep(0.1)
            self.push_change_event("State", self.dev_state())
        # TBD: Dish mode change
        return ([ResultCode.OK], [""])

    def is_Off_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Off(self):
        # Set device state
        if self.dev_state() != DevState.OFF:
            self.set_state(DevState.OFF)
            time.sleep(0.1)
            self.push_change_event("State", self.dev_state())
        # TBD: Dish mode change
        return ([ResultCode.OK], [""])

    def is_SetStandbyFPMode_allowed(self):
        return True

    def is_Standby_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Standby(self):
        # Set the device state
        if self.dev_state() != DevState.STANDBY:
            self.set_state(DevState.STANDBY)
            time.sleep(0.1)
            self.push_change_event("State", self.dev_state())
        # Set the Dish Mode
        self.set_dish_mode(DishMode.STANDBY_LP)
        return ([ResultCode.OK], [""])

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetStandbyFPMode(self):
        # import debugpy; debugpy.debug_this_thread()'
        self.logger.info("Processing SetStandbyFPMode Command")
        # Set the Device State
        if self.dev_state() != DevState.STANDBY:
            self.set_state(DevState.STANDBY)
            time.sleep(0.1)
            self.push_change_event("State", self.dev_state())
        # Set the Dish Mode
        self.set_dish_mode(DishMode.STANDBY_FP)
        return ([ResultCode.OK], [""])

    def is_SetStandbyLPMode_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetStandbyLPMode(self):
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

    def is_SetOperateMode_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetOperateMode(self):
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

    def is_SetStowMode_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetStowMode(self):
        self.logger.info("Processing SetStowMode Command")
        # Set device state
        if self.dev_state() != DevState.DISABLE:
            self.set_state(DevState.DISABLE)
            time.sleep(0.1)
            self.push_change_event("State", self.dev_state())
        # Set dish mode
        self.set_dish_mode(DishMode.STOW)
        return ([ResultCode.OK], [""])

    def is_Track_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Track(self):
        self.logger.info("Processing Track Command")
        if self._pointing_state != PointingState.TRACK:
            self._pointing_state = PointingState.TRACK
            self.push_change_event("pointingState", self._pointing_state)
        # Set dish mode
        self.set_dish_mode(DishMode.OPERATE)
        return ([ResultCode.OK], [""])

    def is_TrackStop_allowed(self):
        return True

    @command(
        dtype_in="DevVoid",
        doc_out="(ReturnType, 'DevVoid')",
    )
    def TrackStop(self):
        self.logger.info("Processing TrackStop Command")
        # Set dish mode
        self.set_dish_mode(DishMode.OPERATE)

    def is_AbortCommands_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def AbortCommands(self):
        self.logger.info("Abort Completed")
        # Dish Mode Not Applicable.
        return ([ResultCode.OK], [""])

    def is_ConfigureBand1_allowed(self):
        return True

    @command(
        dtype_in=("DevString"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def ConfigureBand1(self, argin):
        self.logger.info("Processing ConfigureBand1")
        # Set dish mode
        self.set_dish_mode(DishMode.CONFIG)

    def is_ConfigureBand2_allowed(self):
        return True

    @command(
        dtype_in=("DevString"),
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'DevVarLongStringArray')",
    )
    def ConfigureBand2(self, argin):
        self.logger.info("Processing ConfigureBand2")
        # Set dish mode
        self.set_dish_mode(DishMode.CONFIG)
        return ([ResultCode.OK], [""])

    def is_ConfigureBand3_allowed(self):
        return True

    @command(
        dtype_in=("DevString"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def ConfigureBand3(self, argin):
        self.logger.info("Processing ConfigureBand3")
        # Set dish mode
        self.set_dish_mode(DishMode.CONFIG)

    def is_ConfigureBand4_allowed(self):
        return True

    @command(
        dtype_in=("DevString"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def ConfigureBand4(self, argin):
        self.logger.info("Processing ConfigureBand4")
        # Set dish mode
        self.set_dish_mode(DishMode.CONFIG)

    def is_ConfigureBand5a_allowed(self):
        return True

    @command(
        dtype_in=("DevString"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def ConfigureBand5a(self, argin):
        self.logger.info("Processing ConfigureBand5a")
        # Set dish mode
        self.set_dish_mode(DishMode.CONFIG)

    def is_ConfigureBand5b_allowed(self):
        return True

    @command(
        dtype_in=("DevString"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def ConfigureBand5b(self, argin):
        self.logger.info("Processing ConfigureBand5")
        # Set dish mode
        self.set_dish_mode(DishMode.CONFIG)

    @command(
        dtype_in=("DevVarDoubleArray"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def Slew(self):
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

    @command(
        dtype_in=("DevVoid"),
        doc_out="(ReturnType, 'DevVoid')",
    )
    def Scan(self):
        # TBD: Dish mode change
        pass

    @command(
        dtype_in=("DevVoid"),
        doc_out="(ReturnType, 'informational message')",
    )
    def Reset(self):
        # TBD: Dish mode change
        return ([ResultCode.OK], [""])
