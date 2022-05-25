from ska_tango_base.base import OpStateModel
from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.base.component_manager import BaseComponentManager
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import HealthState
from tango import DevState
from tango.server import command


class EmptyComponentManager(BaseComponentManager):
    def __init__(self, op_state_model, logger=None, *args, **kwargs):
        self.logger = logger
        super().__init__(op_state_model, *args, **kwargs)


class HelperCspMasterDevice(SKABaseDevice):
    """A helper device for triggering state changes with a command on CspMaster."""

    def init_device(self):
        super().init_device()
        self._health_state = HealthState.OK

    class InitCommand(SKABaseDevice.InitCommand):
        def do(self):
            super().do()
            device = self.target
            device.set_change_event("State", True, False)
            device.set_change_event("healthState", True, False)
            return (ResultCode.OK, "")

    def create_component_manager(self):
        self.op_state_model = OpStateModel(
            logger=self.logger, callback=super()._update_state
        )
        cm = EmptyComponentManager(self.op_state_model, logger=self.logger)
        return cm

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
        dtype_in="DevVarStringArray",
        doc_in="Input argument",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def On(self, argin):
        if self.dev_state() != DevState.ON:
            self.set_state(DevState.ON)
        return [[ResultCode.OK], [""]]

    def is_Off_allowed(self):
        return True

    @command(
        dtype_in="DevVarStringArray",
        doc_in="Input argument",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Off(self, argin):
        if self.dev_state() != DevState.OFF:
            self.set_state(DevState.OFF)
        return [[ResultCode.OK], [""]]

    def is_Standby_allowed(self):
        return True

    @command(
        dtype_in="DevVarStringArray",
        doc_in="Input argument",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Standby(self, argin):
        if self.dev_state() != DevState.STANDBY:
            self.set_state(DevState.STANDBY)
        return [[ResultCode.OK], [""]]
