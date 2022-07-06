import logging
from typing import Callable

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import HealthState, ObsState
from ska_tango_base.subarray import SKASubarray, SubarrayComponentManager
from tango import AttrWriteType, DevState
from tango.server import attribute, command


class EmptySubArrayComponentManager(SubarrayComponentManager):
    def __init__(
        self,
        logger: logging.Logger,
        communication_state_callback: Callable,
        component_state_callback: Callable,
        **state
    ):
        self.logger = logger
        super().__init__(
            logger,
            communication_state_callback,
            component_state_callback,
            **state
        )
        self._assigned_resources = []

    def assign(self, resources):
        """
        Assign resources to the component.

        :param resources: resources to be assign
        """
        self.logger.info("Resources: %s", resources)
        self._assigned_resources = ["0001"]
        return (ResultCode.OK, "")

    def release(self, resources):
        """
        Release resources from the component.

        :param resources: resources to be released
        """
        return (ResultCode.OK, "")

    def release_all(self):
        """Release all resources."""
        self._assigned_resources = []

        return (ResultCode.OK, "")

    def configure(self, configuration):
        """
        Configure the component.

        :param configuration: the configuration to be configured
        :type configuration: dict
        """
        self.logger("%s", configuration)

        return (ResultCode.OK, "")

    def scan(self, args):
        """Start scanning."""
        self.logger("%s", args)
        return (ResultCode.OK, "")

    def end_scan(self):
        """End scanning."""

        return (ResultCode.OK, "")

    def end(self):
        """End Scheduling blocks."""

        return (ResultCode.OK, "")

    def abort(self):
        """Tell the component to abort whatever it was doing."""

        return (ResultCode.OK, "")

    def obsreset(self):
        """Reset the component to unconfigured but do not release resources."""

        return (ResultCode.OK, "")

    def restart(self):
        """Deconfigure and release all resources."""

        return (ResultCode.OK, "")

    @property
    def assigned_resources(self):
        """
        Return the resources assigned to the component.

        :return: the resources assigned to the component
        :rtype: list of str
        """
        # import debugpy; debugpy.debug_this_thread()
        return self._assigned_resources


class HelperSubArrayDevice(SKASubarray):
    """A generic subarray device for triggering state changes with a command.
    It can be used as helper device for element subarray node"""

    def init_device(self):
        super().init_device()
        self._health_state = HealthState.OK
        self._command_in_progress = ""

    class InitCommand(SKASubarray.InitCommand):
        def do(self):
            super().do()
            self._device._receive_addresses = '{"science_A":{"host":[[0,"192.168.0.1"],[2000,"192.168.0.1"]],"port":[[0,9000,1],[2000,9000,1]]}}'
            self._device.set_change_event("State", True, False)
            self._device.set_change_event("obsState", True, False)
            self._device.set_change_event("commandInProgress", True, False)
            self._device.set_change_event("healthState", True, False)
            self._device.set_change_event("receiveAddresses", True, False)
            return (ResultCode.OK, "")

    commandInProgress = attribute(dtype="DevString", access=AttrWriteType.READ)

    receiveAddresses = attribute(dtype="DevString", access=AttrWriteType.READ)

    def read_receiveAddresses(self):
        return self._receive_addresses

    def read_commandInProgress(self):
        return self._command_in_progress

    def create_component_manager(self):
        cm = EmptySubArrayComponentManager(
            logger=self.logger,
            communication_state_callback=None,
            component_state_callback=None,
        )
        return cm

    @command(
        dtype_in=int,
        doc_in="Set ObsState",
    )
    def SetDirectObsState(self, argin):
        """
        Trigger a ObsState change
        """
        # import debugpy; debugpy.debug_this_thread()
        value = ObsState(argin)
        if self._obs_state != value:
            self._obs_state = value
            self.push_change_event("obsState", self._obs_state)

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
        # # pylint: disable=E0203
        value = HealthState(argin)
        if self._health_state != value:
            self._health_state = HealthState(argin)
            self.push_change_event("healthState", self._health_state)

    @command(
        dtype_in="DevString",
        doc_in="command in progress",
    )
    def SetDirectCommandInProgress(self, argin):
        """
        Trigger a CommandInProgress change
        """
        # import debugpy; debugpy.debug_this_thread()
        if self._command_in_progress != argin:
            self._command_in_progress = argin
            self.push_change_event(
                "commandInProgress", self._command_in_progress
            )

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

    def is_AssignResources_allowed(self):
        """
        Check if command `AssignResources` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format consists of receptorIDList.",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def AssignResources(self, argin):
        if self._obs_state != ObsState.IDLE:
            self._obs_state = ObsState.IDLE
            self.push_change_event("obsState", self._obs_state)
        return [[ResultCode.OK], [""]]

    def is_ReleaseResources_allowed(self):
        """
        Check if command `ReleaseResources` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ReleaseResources(self):
        if self._obs_state != ObsState.EMPTY:
            self._obs_state = ObsState.EMPTY
            self.push_change_event("obsState", self._obs_state)
        return [[ResultCode.OK], [""]]

    def is_ReleaseAllResources_allowed(self):
        """
        Check if command `ReleaseAllResources` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ReleaseAllResources(self):
        if self._obs_state != ObsState.EMPTY:
            self._obs_state = ObsState.EMPTY
            self.push_change_event("obsState", self._obs_state)
        return [[ResultCode.OK], [""]]

    def is_Configure_allowed(self):
        """
        Check if command `Configure` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format.",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Configure(self, argin):
        if self._obs_state != ObsState.READY:
            self._obs_state = ObsState.READY
            self.push_change_event("obsState", self._obs_state)
        return [[ResultCode.OK], [""]]

    def is_Scan_allowed(self):
        """
        Check if command `Scan` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format.",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Scan(self, argin):
        if self._obs_state != ObsState.SCANNING:
            self._obs_state = ObsState.SCANNING
            self.push_change_event("obsState", self._obs_state)
        return [[ResultCode.OK], [""]]

    def is_EndScan_allowed(self):
        """
        Check if command `EndScan` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def EndScan(self):
        if self._obs_state != ObsState.READY:
            self._obs_state = ObsState.READY
            self.push_change_event("obsState", self._obs_state)
        return [[ResultCode.OK], [""]]

    def is_End_allowed(self):
        """
        Check if command `End` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def End(self):
        if self._obs_state != ObsState.IDLE:
            self._obs_state = ObsState.IDLE
            self.push_change_event("obsState", self._obs_state)
        return [[ResultCode.OK], [""]]

    def is_ObsReset_allowed(self):
        """
        Check if command `ObsReset` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ObsReset(self):
        if self._obs_state != ObsState.IDLE:
            self._obs_state = ObsState.IDLE
            self.push_change_event("obsState", self._obs_state)
        return [[ResultCode.OK], [""]]

    def is_Abort_allowed(self):
        """
        Check if command `Abort` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Abort(self):
        if self._obs_state != ObsState.ABORTED:
            self._obs_state = ObsState.ABORTED
            self.push_change_event("obsState", self._obs_state)
        return [[ResultCode.OK], [""]]

    def is_Restart_allowed(self):
        """
        Check if command `Restart` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Restart(self):
        if self._obs_state != ObsState.EMPTY:
            self._obs_state = ObsState.EMPTY
            self.push_change_event("obsState", self._obs_state)
        return [[ResultCode.OK], [""]]
