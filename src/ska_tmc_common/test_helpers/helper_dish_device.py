from ska_tango_base.base import OpStateModel
from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.base.component_manager import BaseComponentManager
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import HealthState
from tango import AttrWriteType, DevState
from tango.server import attribute, command

from ska_tmc_common.enum import PointingState


class EmptyComponentManager(BaseComponentManager):
    def __init__(self, op_state_model, logger=None, *args, **kwargs):
        self.logger = logger
        super().__init__(op_state_model, *args, **kwargs)


class HelperDishDevice(SKABaseDevice):
    """A device exposing commands and attributes of the Dish device."""

    def init_device(self):
        super().init_device()
        self._health_state = HealthState.OK
        self._pointing_state = PointingState.NONE

    class InitCommand(SKABaseDevice.InitCommand):
        def do(self):
            super().do()
            device = self.target
            # device._pointing_state = PointingState.NONE
            device.set_change_event("State", True, False)
            device.set_change_event("healthState", True, False)
            device.set_change_event("pointingState", True, False)
            return (ResultCode.OK, "")

    pointingState = attribute(dtype=PointingState, access=AttrWriteType.READ)

    def read_pointingState(self):
        return self._pointing_state

    def create_component_manager(self):
        self.op_state_model = OpStateModel(
            logger=self.logger, callback=super()._update_state
        )
        cm = EmptyComponentManager(self.op_state_model, logger=self.logger)
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

    def is_On_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def On(self):
        if self.dev_state() != DevState.ON:
            self.set_state(DevState.ON)
        return [[ResultCode.OK], [""]]

    def is_Off_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Off(self):
        if self.dev_state() != DevState.OFF:
            self.set_state(DevState.OFF)
        return [[ResultCode.OK], [""]]

    def is_SetStandbyFPMode_allowed(self):
        return True

    def is_Standby_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Standby(self):
        if self.dev_state() != DevState.STANDBY:
            self.set_state(DevState.STANDBY)
        return [[ResultCode.OK], [""]]

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetStandbyFPMode(self):
        # import debugpy; debugpy.debug_this_thread()
        return [[ResultCode.OK], [""]]

    def is_SetStandbyLPMode_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetStandbyLPMode(self):
        if self.dev_state() != DevState.OFF:
            self.set_state(DevState.OFF)
        return [[ResultCode.OK], [""]]

    def is_SetOperateMode_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetOperateMode(self):
        if self.dev_state() != DevState.ON:
            self.set_state(DevState.ON)
        return [[ResultCode.OK], [""]]

    def is_SetStowMode_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetStowMode(self):
        return [[ResultCode.OK], [""]]

    def is_Configure_allowed(self):
        return True

    @command(
        dtype_in=("str"),
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Configure(self, argin):
        self.logger.info("Configure Completed...")
        return [[ResultCode.OK], [""]]

    def is_Track_allowed(self):
        return True

    @command(
        dtype_in=("str"),
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Track(self, argin):
        self.logger.info("Track Completed...")
        return [[ResultCode.OK], [""]]

    def is_StopTrack_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def StopTrack(self):
        self.logger.info("StopTrack Completed...")
        return [[ResultCode.OK], [""]]

    def is_Abort_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Abort(self):
        self.logger.info("Abort Completed...")
        return [[ResultCode.OK], [""]]

    def is_ObsReset_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ObsReset(self):
        self.logger.info("ObsReset Completed...")
        return [[ResultCode.OK], [""]]

    def is_Restart_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Restart(self):
        self.logger.info("Restart Completed...")
        return [[ResultCode.OK], [""]]
