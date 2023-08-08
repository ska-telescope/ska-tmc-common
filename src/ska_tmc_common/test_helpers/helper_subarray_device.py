"""
This module implements the Helper devices for subarray nodes for testing
an integrated TMC
"""
import json

# pylint: disable=attribute-defined-outside-init
import threading
import time
from logging import Logger
from typing import Any, Callable, List, Optional, Tuple

import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import HealthState, ObsState
from ska_tango_base.subarray import SKASubarray, SubarrayComponentManager
from tango import AttrWriteType, DevState, EnsureOmniThread
from tango.server import attribute, command, run

from .constants import (
    ABORT,
    ASSIGN_RESOURCES,
    CONFIGURE,
    END,
    END_SCAN,
    GO_TO_IDLE,
    OBS_RESET,
    OFF,
    ON,
    RELEASE_ALL_RESOURCES,
    RELEASE_RESOURCES,
    RESTART,
    SCAN,
    STAND_BY,
)

MAX_REPORTED_COMMANDS = 15


class EmptySubArrayComponentManager(SubarrayComponentManager):
    """
    This is a Component Manager created for the use of Helper Subarray devices.
    """

    def __init__(
        self,
        logger: Logger,
        communication_state_callback: Optional[Callable],
        component_state_callback: Optional[Callable],
        **kwargs,
    ) -> None:
        self.logger = logger
        super().__init__(
            logger,
            communication_state_callback,
            component_state_callback,
            **kwargs,
        )
        self._assigned_resources = []

    def assign(self, resources: list) -> Tuple[ResultCode, str]:
        """
        Assign resources to the component.
        :param resources: resources to be assigned
        :returns: ResultCode, message
        :rtype:tuple
        """
        self.logger.info("Resources: %s", resources)
        self._assigned_resources = ["0001"]
        return ResultCode.OK, ""

    def release(self, resources: list) -> Tuple[ResultCode, str]:
        """
        Release resources from the component.
        :param resources: resources to be released
        :returns: ResultCode, message
        :rtype:tuple
        """
        return ResultCode.OK, ""

    def release_all(self) -> Tuple[ResultCode, str]:
        """
        Release all resources.
        :returns: ResultCode, message
        :rtype:tuple
        """
        self._assigned_resources = []

        return ResultCode.OK, ""

    def configure(self, configuration: str) -> Tuple[ResultCode, str]:
        """
        Configure the component.
        :param configuration: the configuration to be configured
        :type configuration: dict
        :returns: ResultCode, message
        :rtype:tuple
        """
        self.logger.info("%s", configuration)

        return ResultCode.OK, ""

    def scan(self, args: Any) -> Tuple[ResultCode, str]:
        """
        Start scanning.
        :returns: ResultCode, message
        :rtype:tuple
        """
        self.logger.info("%s", args)
        return ResultCode.OK, ""

    def end_scan(self) -> Tuple[ResultCode, str]:
        """
        End scanning.
        :returns: ResultCode, message
        :rtype:tuple
        """

        return ResultCode.OK, ""

    def end(self) -> Tuple[ResultCode, str]:
        """
        End Scheduling blocks.
        :returns: ResultCode, message
        :rtype:tuple
        """

        return ResultCode.OK, ""

    def abort(self) -> Tuple[ResultCode, str]:
        """
        Tell the component to abort whatever it was doing.
        :returns: ResultCode, message
        :rtype:tuple
        """

        return ResultCode.OK, ""

    def obsreset(self) -> Tuple[ResultCode, str]:
        """
        Reset the component to unconfirmed but do not release resources.
        :returns: ResultCode, message
        :rtype:tuple
        """

        return ResultCode.OK, ""

    def restart(self) -> Tuple[ResultCode, str]:
        """
        Deconfigure and release all resources.
        :returns: ResultCode, message
        :rtype:tuple
        """

        return ResultCode.OK, ""

    @property
    def assigned_resources(self) -> list:
        """
        Return the resources assigned to the component.

        :return: the resources assigned to the component
        :rtype: list of str
        """
        # import debugpy; debugpy.debug_this_thread()
        return self._assigned_resources


# pylint: disable=too-many-instance-attributes
class HelperSubArrayDevice(SKASubarray):
    """A generic subarray device for triggering state changes with a command.
    It can be used as helper device for element subarray node"""

    def init_device(self):
        super().init_device()
        # super(SKASubarray, self).init_device()
        self._health_state = HealthState.OK
        self._command_in_progress = ""
        self._defective = False
        self._command_delay_info = {
            ASSIGN_RESOURCES: 2,
            CONFIGURE: 2,
            RELEASE_RESOURCES: 2,
            ABORT: 2,
            RESTART: 2,
            RELEASE_ALL_RESOURCES: 2,
            END: 2,
        }
        self._raise_exception = False
        # tuple of list
        self._command_call_info = []
        self._command_info = ("", "")
        self._state_duration_info = []

    class InitCommand(SKASubarray.InitCommand):
        """A class for the HelperSubarrayDevice's init_device() "command"."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            """
            super().do()
            self._device.set_change_event("State", True, False)
            self._device.set_change_event("obsState", True, False)
            self._device.set_change_event("commandInProgress", True, False)
            self._device.set_change_event("healthState", True, False)
            self._device.set_change_event(
                "longRunningCommandResult", True, False
            )
            self._device.set_change_event("commandCallInfo", True, False)
            return ResultCode.OK, ""

    commandInProgress = attribute(dtype="DevString", access=AttrWriteType.READ)

    receiveAddresses = attribute(dtype="DevString", access=AttrWriteType.READ)

    defective = attribute(dtype=str, access=AttrWriteType.READ)

    commandDelayInfo = attribute(dtype=str, access=AttrWriteType.READ)

    raiseException = attribute(dtype=bool, access=AttrWriteType.READ)

    commandCallInfo = attribute(
        dtype=(("str",),),
        access=AttrWriteType.READ,
        max_dim_x=100,
        max_dim_y=100,
    )

    obsStateTransitionDuration = attribute(
        dtype="DevString", access=AttrWriteType.READ
    )

    def read_obsStateTransitionDuration(self):
        """Read transition"""
        return json.dumps(self._state_duration_info)

    @command(
        dtype_in=str,
        doc_in="Set Obs State Duration",
    )
    def AddTransition(self, state_duration_info: str) -> None:
        """This command will set duration for obs state such that when
        respective command for obs state is triggered then it change obs state
        after provided duration
        """
        self.logger.info(
            "Adding observation state transitions for Csp Subarray and \
                         Sdp Subarray Simulators"
        )
        self.logger.info(
            "ObsState transitions sequence for Csp Subarray and \
                Sdp Subarray Simulators is: %s",
            state_duration_info,
        )
        self._state_duration_info = json.loads(state_duration_info)

    @command(
        doc_in="Reset Obs State Duration",
    )
    def ResetTransitions(self) -> None:
        """This command will reset ObsState duration which is set"""
        self.logger.info("Resetting Obs State Duration")
        self._state_duration_info = []

    def read_commandCallInfo(self):
        """This method is used to read the attribute value for
        commandCallInfo.
        """
        return self._command_call_info

    def read_commandDelayInfo(self):
        """This method is used to read the attribute value for delay."""

        return json.dumps(self._command_delay_info)

    def read_raiseException(self) -> bool:
        """This method is used to read the attribute value for raise exception

        :rtype: bool
        """
        return self._raise_exception

    def read_commandInProgress(self) -> str:
        """
        This method is used to read, which command is in progress
        :rtype:str
        """
        return self._command_in_progress

    def read_defective(self) -> bool:
        """
        This method is used to read the value of the attribute defective
        :rtype:bool
        """
        return self._defective

    def read_receiveAddresses(self) -> str:
        """
        This method is used to read receiveAddresses attribute
        :rtype:str
        """
        return self._receive_addresses

    def update_device_obsstate(
        self, value: ObsState, command_name: str = ""
    ) -> None:
        """Updates the given data after a delay."""
        delay_value = 0
        with tango.EnsureOmniThread():
            if command_name in self._command_delay_info:
                delay_value = self._command_delay_info[command_name]
            time.sleep(delay_value)
            self.logger.info(
                "Sleep %s for command %s ", delay_value, command_name
            )
            self._obs_state = value
            time.sleep(0.1)
            self.push_change_event("obsState", self._obs_state)

    def update_command_info(
        self, command_name: str = "", command_input: str = ""
    ) -> None:
        """This method updates the commandCallInfo attribute,
        with the respective command information.

        Args:
            command_name (str): command name
            command_input (str): Input argin for command
        """
        self.logger.info(
            "Recording the command data for Sdp Subarray \
                 or Csp Subarray simulators"
        )
        self._command_info = (command_name, command_input)
        self.logger.info(
            "Recorded command_info for Sdp Subarray \
            or Csp Subarray simulators is %s",
            self._command_info,
        )
        self._command_call_info.append(self._command_info)
        self.logger.info(
            "Recorded command_call_info list for Csp Subarray or \
                Sdp Subarray simulators is %s",
            self._command_call_info,
        )
        self.push_change_event("commandCallInfo", self._command_call_info)
        self.logger.info("CommandCallInfo updates are pushed")

    def _update_obs_state_in_sequence(self):
        """Update Obs state in sequence as per state duration info"""
        with tango.EnsureOmniThread():
            for obs_state, duration in self._state_duration_info:
                obs_state_enum = ObsState[obs_state]
                self.logger.info(
                    "Sleep %s for obs state %s", duration, obs_state
                )
                time.sleep(duration)
                self._obs_state = obs_state_enum
                self.push_change_event("obsState", self._obs_state)

    def _start_thread(self, args: list) -> None:
        """This method start thread which is required for
        changing obs state after certain duration
        """
        thread = threading.Thread(
            target=self.update_device_obsstate,
            args=args,
        )
        thread.start()

    def _follow_state_duration(self):
        """This method will update obs state as per state duration
        in separate thread
        """
        thread = threading.Thread(
            target=self._update_obs_state_in_sequence,
        )
        thread.start()

    def create_component_manager(self) -> EmptySubArrayComponentManager:
        """
        This method is used to create an instance of
        EmptySubarrayComponentManager         :return:
        :rtype: class
        """
        cm = EmptySubArrayComponentManager(
            logger=self.logger,
            communication_state_callback=None,
            component_state_callback=None,
        )
        return cm

    @command(
        dtype_in=bool,
        doc_in="Set Defective",
    )
    def SetDefective(self, values: str) -> None:
        """
        Trigger defective change
        :rtype: bool
        """
        """
        Trigger defective change
        :param: values
        :type: str
        """
        input_dict = json.loads(values)
        self.logger.info("Setting defective params to %s", input_dict)
        for key, value in input_dict.items():
            self.defective_params[key] = value

    @command(
        dtype_in=bool,
        doc_in="Raise Exception",
    )
    def SetRaiseException(self, value: bool) -> None:
        """Set Raise Exception"""
        self.logger.info("Setting the raise exception value to : %s", value)
        self._raise_exception = value

    @command(
        dtype_in=str,
        doc_in="Set Delay",
    )
    def SetDelay(self, command_delay_info: str) -> None:
        """Update delay value"""
        self.logger.info(
            "Setting the Delay value for Csp Subarray \
                or Sdp Subarray simulator to : %s",
            command_delay_info,
        )
        # set command info
        command_delay_info_dict = json.loads(command_delay_info)
        for key, value in command_delay_info_dict.items():
            self._command_delay_info[key] = value
        self.logger.info("Command Delay Info Set %s", self._command_delay_info)

    @command(
        doc_in="Reset Delay",
    )
    def ResetDelay(self) -> None:
        """Reset Delay to it's default values"""
        self.logger.info(
            "Resetting Command Delays for \
            Csp Subarray or Sdp Simulators"
        )
        # Reset command info
        self._command_delay_info = {
            ASSIGN_RESOURCES: 2,
            CONFIGURE: 2,
            RELEASE_RESOURCES: 2,
            ABORT: 2,
            RESTART: 2,
            RELEASE_ALL_RESOURCES: 2,
            END: 2,
        }

    @command(
        doc_in="Clears commandCallInfo",
    )
    def ClearCommandCallInfo(self) -> None:
        """Clears commandCallInfo to empty list"""
        self.logger.info(
            "Clearing CommandCallInfo for Csp and Sdp Subarray simulators"
        )
        self._command_call_info.clear()
        self.push_change_event("commandCallInfo", self._command_call_info)

    @command(
        dtype_in=int,
        doc_in="Set ObsState",
    )
    def SetDirectObsState(self, argin: ObsState) -> None:
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
    def SetDirectState(self, argin: tango.DevState) -> None:
        """
        Trigger a DevStateif self.dev_state() != argin:
            self.set_state(argin)
                change
        """
        # import debugpy; debugpy.debug_this_thread()
        if self.dev_state() != argin:
            self.set_state(argin)
            self.push_change_event("State", self.dev_state())

    @command(
        dtype_in=int,
        doc_in="state to assign",
    )
    def SetDirectHealthState(self, argin: HealthState) -> None:
        """
        Trigger a HealthState change
        """
        # import debugpy; debugpy.debug_this_thread()
        # # pylint: disable=E0203
        self.logger.info(
            "HealthState value for simulator is : %s", self._health_state
        )
        value = HealthState(argin)
        if self._health_state != value:
            self.logger.info(
                "Setting HealthState value for simulator to : %s", value
            )
            self._health_state = HealthState(argin)
            self.push_change_event("healthState", self._health_state)
            self.logger.info("Pushed updated HealthState value for simulator")

    @command(
        dtype_in="DevString",
        doc_in="command in progress",
    )
    def SetDirectCommandInProgress(self, argin: str) -> None:
        """
        Trigger a CommandInProgress change
        """
        # import debugpy; debugpy.debug_this_thread()
        if self._command_in_progress != argin:
            self._command_in_progress = argin
            self.push_change_event(
                "commandInProgress", self._command_in_progress
            )

    def is_On_allowed(self) -> bool:
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def On(self) -> Tuple[List[ResultCode], List[str]]:
        self.update_command_info(ON, "")

        if not self._defective:
            if self.dev_state() != DevState.ON:
                self.set_state(DevState.ON)
                self.push_change_event("State", self.dev_state())
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]

    def is_Off_allowed(self) -> bool:
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Off(self) -> Tuple[List[ResultCode], List[str]]:
        self.update_command_info(OFF, "")

        if not self._defective:
            if self.dev_state() != DevState.OFF:
                self.set_state(DevState.OFF)
                self.push_change_event("State", self.dev_state())
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]

    def is_Standby_allowed(self) -> bool:
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Standby(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes Standby command on subarray devices
        :return: ResultCode, message
        :rtype: tuple
        """
        self.update_command_info(STAND_BY, "")

        if not self._defective:
            if self.dev_state() != DevState.STANDBY:
                self.set_state(DevState.STANDBY)
                self.push_change_event("State", self.dev_state())
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]

    def is_AssignResources_allowed(self) -> bool:
        """
        Check if command `AssignResources` is allowed in the current device
        state.

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
    def AssignResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes AssignResources command on subarray devices
        """
        self.update_command_info(ASSIGN_RESOURCES, argin)

        if self._defective:
            self._obs_state = ObsState.RESOURCING
            self.push_change_event("obsState", self._obs_state)
            return [ResultCode.FAILED], [
                "Device is defective, cannot process command.completely."
            ]

        if self._raise_exception:
            self._obs_state = ObsState.RESOURCING
            self.push_change_event("obsState", self._obs_state)
            self.thread = threading.Thread(
                target=self.wait_and_update_exception, args=["AssignResources"]
            )
            self.thread.start()
            return [ResultCode.QUEUED], [""]

        self._obs_state = ObsState.RESOURCING
        self.push_change_event("obsState", self._obs_state)
        thread = threading.Thread(
            target=self.update_device_obsstate,
            args=[ObsState.IDLE, ASSIGN_RESOURCES],
        )
        thread.start()
        return [ResultCode.OK], [""]

    def wait_and_update_exception(self, command_name):
        """Waits for 5 secs before pushing a longRunningCommandResult event."""
        with EnsureOmniThread():
            time.sleep(5)
            command_id = f"1000_{command_name}"
            command_result = (
                command_id,
                f"Exception occured on device: {self.get_name()}",
            )
            self.push_change_event("longRunningCommandResult", command_result)

    def is_ReleaseResources_allowed(self) -> bool:
        """
        Check if command `ReleaseResources` is allowed in the current device
        state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ReleaseResources(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes ReleaseResources command on subarray device
        """
        self.update_command_info(RELEASE_RESOURCES, "")

        if not self._defective:
            if self._obs_state != ObsState.EMPTY:
                self._obs_state = ObsState.EMPTY
                self.push_change_event("obsState", self._obs_state)
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]

    def is_ReleaseAllResources_allowed(self) -> bool:
        """
        Check if command `ReleaseAllResources` is allowed in the current
        device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ReleaseAllResources(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes ReleaseAllResources command on
        subarray device
        :return: ResultCode, message
        :rtype: tuple
        """
        self.update_command_info(RELEASE_ALL_RESOURCES, "")

        if self._defective:
            self._obs_state = ObsState.RESOURCING
            self.push_change_event("obsState", self._obs_state)
            return [ResultCode.FAILED], [
                "Device is Defective, cannot process command completely."
            ]

        if self._raise_exception:
            self._obs_state = ObsState.RESOURCING
            self.push_change_event("obsState", self._obs_state)
            self.thread = threading.Thread(
                target=self.wait_and_update_exception,
                args=["ReleaseAllResources"],
            )
            self.thread.start()
            return [ResultCode.QUEUED], [""]

        self._obs_state = ObsState.RESOURCING
        self.push_change_event("obsState", self._obs_state)
        thread = threading.Thread(
            target=self.update_device_obsstate,
            args=[ObsState.EMPTY, RELEASE_RESOURCES],
        )
        thread.start()
        return [ResultCode.OK], [""]

    def is_Configure_allowed(self) -> bool:
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
    def Configure(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes Configure command on subarray devices
        :return: ResultCode, message
        :rtype: tuple
        """

        self.update_command_info(CONFIGURE, argin)

        if not self._defective:
            if self._obs_state in [ObsState.READY, ObsState.IDLE]:
                if self._state_duration_info:
                    self._follow_state_duration()
                else:
                    self._obs_state = ObsState.CONFIGURING
                    self.push_change_event("obsState", self._obs_state)
                    self.logger.info("Starting Thread for configure")
                    self._start_thread([ObsState.READY, CONFIGURE])
            return [ResultCode.OK], [""]
        self._obs_state = ObsState.CONFIGURING
        self.push_change_event("obsState", self._obs_state)
        return [ResultCode.FAILED], [
            "Device is defective, cannot process command.completely."
        ]

    def is_Scan_allowed(self) -> bool:
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
    def Scan(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes Scan command on subarray devices.
        :return: ResultCode, message
        :rtype: tuple
        """
        self.update_command_info(SCAN, argin)
        if not self._defective:
            if self._obs_state != ObsState.SCANNING:
                self._obs_state = ObsState.SCANNING
                self.push_change_event("obsState", self._obs_state)
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]

    def is_EndScan_allowed(self) -> bool:
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
    def EndScan(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes EndScan command on subarray devices.
        :return: ResultCode, message
        :rtype: tuple
        """
        self.update_command_info(END_SCAN, "")
        if not self._defective:
            if self._obs_state != ObsState.READY:
                self._obs_state = ObsState.READY
                self.push_change_event("obsState", self._obs_state)
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]

    def is_End_allowed(self) -> bool:
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
    def End(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes End command on subarray devices.
        :return: ResultCode, message
        :rtype: tuple
        """
        self.update_command_info(END, "")
        if not self._defective:
            if self._obs_state != ObsState.IDLE:
                if self._state_duration_info:
                    self._follow_state_duration()
                else:
                    self._obs_state = ObsState.IDLE
                    self.push_change_event("obsState", self._obs_state)
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]

    def is_GoToIdle_allowed(self) -> bool:
        """
        Check if command `GoToIdle` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def GoToIdle(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes GoToIdle command on subarray devices.
        :return: ResultCode, message
        :rtype: tuple
        """
        self.update_command_info(GO_TO_IDLE, "")
        if not self._defective:
            if self._obs_state != ObsState.IDLE:
                self._obs_state = ObsState.IDLE
                self.push_change_event("obsState", self._obs_state)
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]

    def is_ObsReset_allowed(self) -> bool:
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
    def ObsReset(self) -> Tuple[List[ResultCode], List[str]]:
        self.update_command_info(OBS_RESET, "")
        if not self._defective:
            if self._obs_state != ObsState.IDLE:
                self._obs_state = ObsState.IDLE
                self.push_change_event("obsState", self._obs_state)
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]

    def is_Abort_allowed(self) -> bool:
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
    def Abort(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes Abort command on subarray devices.
        :return: ResultCode, message
        :rtype: tuple
        """
        self.update_command_info(ABORT, "")

        if self._obs_state != ObsState.ABORTED:
            self._obs_state = ObsState.ABORTING
            self.push_change_event("obsState", self._obs_state)
            thread = threading.Thread(
                target=self.update_device_obsstate,
                args=[ObsState.ABORTED, ABORT],
            )
            thread.start()
        return [ResultCode.OK], [""]

    def is_Restart_allowed(self) -> bool:
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
    def Restart(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes Restart command on subarray devices
        :return: ResultCode, message
        :rtype: tuple
        """
        self.update_command_info(RESTART, "")

        if self._obs_state != ObsState.EMPTY:
            self._obs_state = ObsState.RESTARTING
            self.push_change_event("obsState", self._obs_state)
            thread = threading.Thread(
                target=self.update_device_obsstate,
                args=[ObsState.EMPTY, RESTART],
            )
            thread.start()
        return [ResultCode.OK], [""]


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """
    Runs the HelperSubArrayDevice Tango device.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: integer. Exit code of the run method.
    """
    return run((HelperSubArrayDevice,), args=args, **kwargs)


if __name__ == "__main__":
    main()
