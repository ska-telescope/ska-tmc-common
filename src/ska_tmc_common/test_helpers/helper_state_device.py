from typing import Optional

from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.base.component_manager import TaskExecutorComponentManager
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import HealthState
from tango import DevState
from tango.server import command


class EmptyComponentManager(TaskExecutorComponentManager):
    def __init__(
        self, logger=None, max_workers: Optional[int] = None, *args, **kwargs
    ):
        self.logger = logger
        super().__init__(max_workers=max_workers, *args, **kwargs)


class HelperStateDevice(SKABaseDevice):
    """A generic device for triggering state changes with a command.
    It can be used as helper device for TMC Master leaf nodes and element Master nodes"""

    def init_device(self):
        super().init_device()
        self._health_state = HealthState.OK

    class InitCommand(SKABaseDevice.InitCommand):
        def do(self):
            super().do()
            device = self._device
            device.set_change_event("State", True, False)
            device.set_change_event("healthState", True, False)
            return (ResultCode.OK, "")

    def create_component_manager(self):
        cm = EmptyComponentManager(logger=self.logger)
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
        doc_in="state to assign",
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

    def is_Disable_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Disable(self):
        if self.dev_state() != DevState.DISABLE:
            self.set_state(DevState.DISABLE)
        return [[ResultCode.OK], [""]]
