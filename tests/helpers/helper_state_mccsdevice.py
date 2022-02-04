import json

from ska_tango_base.base import OpStateModel
from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.base.component_manager import BaseComponentManager
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import HealthState
from tango import AttrWriteType, DevState
from tango.server import attribute, command


class EmptyComponentManager(BaseComponentManager):
    def __init__(self, op_state_model, logger=None, *args, **kwargs):
        self.logger = logger
        super().__init__(op_state_model, *args, **kwargs)


class HelperMCCSStateDevice(SKABaseDevice):
    """A generic device for triggering state changes with a command"""

    def init_device(self):
        super().init_device()
        self._health_state = HealthState.OK

    class InitCommand(SKABaseDevice.InitCommand):
        def do(self):
            super().do()
            device = self.target
            device._assigned_resources = "{ }"
            device.set_change_event("State", True, False)
            device.set_change_event("healthState", True, False)
            return (ResultCode.OK, "")

        # ----------

    assignedResources = attribute(dtype="DevString", access=AttrWriteType.READ)

    def read_assignedResources(self):
        return self._assigned_resources

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

    def is_TelescopeOn_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def TelescopeOn(self):
        if self.dev_state() != DevState.ON:
            self.set_state(DevState.ON)
        return [[ResultCode.OK], [""]]

    def is_TelescopeOff_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def TelescopeOff(self):
        if self.dev_state() != DevState.OFF:
            self.set_state(DevState.OFF)
        return [[ResultCode.OK], [""]]

    def is_TelescopeStandBy_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def TelescopeStandBy(self):
        if self.dev_state() != DevState.STANDBY:
            self.set_state(DevState.STANDBY)
        return [[ResultCode.OK], [""]]

    def is_AssignResources_allowed(self):
        return True

    @command(
        dtype_in="DevString",
        doc_in="JSON-encoded string with the resources to add to subarray",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def AssignResources(self, argin):
        tmpDict = {
            "interface": "https://schema.skatelescope.org/ska-low-mccs-assignedresources/1.0",
            "subarray_beam_ids": [1],
            "station_ids": [[1, 2]],
            "channel_blocks": [3],
        }
        self._assigned_resources = json.dumps(tmpDict)
        return [[ResultCode.OK], [""]]

    def is_ReleaseResources_allowed(self):
        return True

    @command(
        dtype_in="DevString",
        doc_in="JSON-encoded string with the resources to remove from the subarray",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ReleaseResources(self, argin):
        tmpDict = {
            "interface": "https://schema.skatelescope.org/ska-low-mccs-assignedresources/1.0",
            "subarray_beam_ids": [],
            "station_ids": [],
            "channel_blocks": [],
        }
        self._assigned_resources = json.dumps(tmpDict)
        return [[ResultCode.OK], [""]]
