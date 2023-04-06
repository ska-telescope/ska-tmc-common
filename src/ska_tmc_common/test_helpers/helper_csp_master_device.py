from typing import Optional

from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.base.component_manager import BaseComponentManager
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import HealthState
from tango import AttrWriteType, DevState
from tango.server import attribute, command


class EmptyComponentManager(BaseComponentManager):
    def __init__(
        self, logger=None, max_workers: Optional[int] = None, *args, **kwargs
    ):
        super().__init__(
            logger=logger, max_workers=max_workers, *args, **kwargs
        )

    def start_communicating(self):
        """This method is not used by TMC."""
        self.logger.info("Start communicating method called")
        pass

    def stop_communicating(self):
        """This method is not used by TMC."""
        self.logger.info("Stop communicating method called")
        pass


class HelperCspMasterDevice(SKABaseDevice):
    """A helper device for triggering state changes with a command on CspMaster."""

    def init_device(self):
        super().init_device()
        self._health_state = HealthState.OK
        self._defective = False

    class InitCommand(SKABaseDevice.InitCommand):
        def do(self):
            super().do()
            self._device.set_change_event("State", True, False)
            self._device.set_change_event("healthState", True, False)
            return (ResultCode.OK, "")

    defective = attribute(dtype=bool, access=AttrWriteType.READ)

    def read_defective(self):
        return self._defective

    def create_component_manager(self):
        cm = EmptyComponentManager(
            logger=self.logger,
            max_workers=None,
            communication_state_callback=None,
            component_state_callback=None,
        )
        return cm

    @command(
        dtype_in=bool,
        doc_in="Set Defective",
    )
    def SetDefective(self, value: bool):
        """Trigger defective change"""
        self._defective = value

    @command(
        dtype_in="DevState",
        doc_in="state to assign",
    )
    def SetDirectState(self, argin):
        """
        Trigger a DevState change
        """
        # import debugpy; debugpy.debug_this_thread()
        if not self._defective:
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
        if not self._defective:
            value = HealthState(argin)
            if self._health_state != value:
                self._health_state = HealthState(argin)
                self.push_change_event("healthState", self._health_state)

    def is_On_allowed(self):
        return True

    @command(
        dtype_in="DevVarStringArray",
        doc_in="Input argument as an empty list",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def On(self, argin):
        if not self._defective:
            if self.dev_state() != DevState.ON:
                self.set_state(DevState.ON)
                self.push_change_event("State", self.dev_state())
            return [ResultCode.OK], [""]
        else:
            return [ResultCode.FAILED], [
                "Device is Defective, cannot process command."
            ]

    def is_Off_allowed(self):
        return True

    @command(
        dtype_in="DevVarStringArray",
        doc_in="Input argument as an empty list",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Off(self, argin):
        if not self._defective:
            if self.dev_state() != DevState.OFF:
                self.set_state(DevState.OFF)
                self.push_change_event("State", self.dev_state())
            return [ResultCode.OK], [""]
        else:
            return [ResultCode.FAILED], [
                "Device is Defective, cannot process command."
            ]

    def is_Standby_allowed(self):
        return True

    @command(
        dtype_in="DevVarStringArray",
        doc_in="Input argument as an empty list",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Standby(self, argin):
        if not self.defective:
            if self.dev_state() != DevState.STANDBY:
                self.set_state(DevState.STANDBY)
                self.push_change_event("State", self.dev_state())
                return [ResultCode.OK], [""]
        else:
            return [ResultCode.FAILED], [
                "Device is Defective, cannot process command."
            ]
