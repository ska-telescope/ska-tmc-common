"""
This module implements the Helper devices for subarray leaf nodes for testing
an integrated TMC
"""
import json

# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument
import threading
import time
from typing import List, Tuple

import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from tango import DevState
from tango.server import AttrWriteType, attribute, command, run

from ska_tmc_common import CommandNotAllowed, FaultType
from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice

from .constants import (
    ABORT,
    ASSIGN_RESOURCES,
    CONFIGURE,
    END,
    END_SCAN,
    GO_TO_IDLE,
    OFF,
    ON,
    RELEASE_ALL_RESOURCES,
    RELEASE_RESOURCES,
    RESTART,
    SCAN,
    STAND_BY,
)


class HelperSubarrayLeafDevice(HelperBaseDevice):
    """A device exposing commands and attributes of the Subarray Leaf Nodes
    devices."""

    def init_device(self) -> None:
        super().init_device()
        self._delay = 2
        self._obs_state = ObsState.EMPTY
        self._state_duration_info = []
        # list of tuple
        self._command_call_info = []
        self._command_info = ("", "")

    class InitCommand(HelperBaseDevice.InitCommand):
        """A class for the HelperSubarrayDevice's init_device() "command"."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            """
            super().do()
            self._device.set_change_event("obsState", True, False)
            self._device.set_change_event("commandCallInfo", True, False)
            self._device.op_state_model.perform_action("component_on")
            return ResultCode.OK, ""

    defective = attribute(dtype=str, access=AttrWriteType.READ)

    delay = attribute(dtype=int, access=AttrWriteType.READ)

    obsState = attribute(dtype=ObsState, access=AttrWriteType.READ)

    obsStateTransitionDuration = attribute(
        dtype="DevString", access=AttrWriteType.READ
    )

    commandCallInfo = attribute(
        dtype=(("str",),),
        access=AttrWriteType.READ,
        max_dim_x=100,
        max_dim_y=100,
    )

    def read_obsStateTransitionDuration(self):
        """Read transition"""
        return json.dumps(self._state_duration_info)

    def read_commandCallInfo(self):
        """This method is used to read the attribute value for
        commandCallInfo.
        """
        return self._command_call_info

    def read_defective(self) -> str:
        """
        Returns defective status of devices

        :rtype: dict
        """
        return self._defective

    def read_delay(self) -> int:
        """This method is used to read the attribute value for delay."""
        return self._delay

    def read_obsState(self) -> ObsState:
        """This method is used to read the attribute value for obsState."""
        return self._obs_state

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
            "Recorded command_info for Helper Subarray Leaf device %s",
            self._command_info,
        )
        self._command_call_info.append(self._command_info)
        self.logger.info(
            "Recorded command_call_info list for helper subarray leaf device"
            " is %s",
            self._command_call_info,
        )

        self.push_change_event("commandCallInfo", self._command_call_info)
        self.logger.info("CommandCallInfo updates are pushed")

    def _update_obs_state_in_sequence(self):
        """Update Obs state in sequence as per state duration info
        This method update obs state of subarray device as per sequence
        provided in state_duration_info
        Example:
        if state_duration_info is [["READY", 1], ["FAULT", 2]]
        then obsState is updated to READY in 1 sec and after it update
        it to FAULT in 2 sec
        """
        with tango.EnsureOmniThread():
            for obs_state, duration in self._state_duration_info:
                obs_state_enum = ObsState[obs_state]
                self.logger.info(
                    "Sleep %s for obs state %s", duration, obs_state
                )
                time.sleep(duration)
                self._obs_state = obs_state_enum
                self.push_change_event("obsState", self._obs_state)

    def _follow_state_duration(self):
        """This method will update obs state as per state duration
        in separate thread.
        To avoid Tango default 3 sec timeout creating seperate thread
        for updating obs state.As Updating Obs state might take
        more than 3 sec.
        """
        thread = threading.Thread(
            target=self._update_obs_state_in_sequence,
        )
        thread.start()

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
        dtype_in=str,
        doc_in="Set Obs State Duration",
    )
    def AddTransition(self, state_duration_info: str) -> None:
        """This command will establish a duration for the observation state,
        so that when the corresponding command for the observation state is
        triggered,it will transition to a provided observation state after
        the specified duration
        """
        self.logger.info(
            "Adding observation state transitions for Helper "
            "Subarray Leaf Device"
        )
        self.logger.info(
            "ObsState transitions sequence for "
            "Helper Subarray Leaf Device is: %s",
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

    @command(
        dtype_in=int,
        doc_in="Set Defective parameters",
    )
    def SetDirectObsState(self, value: ObsState) -> None:
        """
        Trigger defective change
        :param: values
        :type: str
        """
        self.logger.info("Setting device obsState to %s", value)
        self._obs_state = ObsState(value)
        self.push_change_event("obsState", self._obs_state)

    @command(
        dtype_in=int,
        doc_in="Set Delay",
    )
    def SetDelay(self, value: int) -> None:
        """Update delay value"""
        self.logger.info(
            "Setting the Delay for CspSubarrayLeafNode \
            and SdpSubarrayLeafNode simulator to : %s",
            value,
        )
        self._delay = value

    def push_command_result(
        self, result: ResultCode, command: str, exception: str = ""
    ) -> None:
        """Push long running command result event for given command.

        :params:

        result: The result code to be pushed as an event
        dtype: ResultCode

        command: The command name for which the event is being pushed
        dtype: str

        exception: Exception message to be pushed as an event
        dtype: str
        """
        command_id = f"{time.time()}-{command}"
        if exception:
            command_result = (command_id, exception)
            self.push_change_event("longRunningCommandResult", command_result)
        command_result = (command_id, json.dumps(result))
        self.push_change_event("longRunningCommandResult", command_result)

    def push_obs_state_event(self, obs_state: ObsState) -> None:
        """Push Obs State Change Event"""
        self.logger.info(
            "Pushing change event for HelperSubarrayLeafDeviceObsState: %s",
            obs_state,
        )
        self._obs_state = obs_state
        self.push_change_event("obsState", self._obs_state)

    def update_device_obsstate(self, obs_state: ObsState):
        """Updates the device obsState"""
        with tango.EnsureOmniThread():
            self._obs_state = obs_state
            time.sleep(0.1)
            self.push_obs_state_event(self._obs_state)

    def is_On_allowed(self) -> bool:
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("On Command is allowed")
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def On(self) -> Tuple[List[ResultCode], List[str]]:
        self.update_command_info(ON)
        if self.defective_params["enabled"]:
            return self.induce_fault(
                "On",
            )

        self.set_state(DevState.ON)
        self.push_change_event("State", self.dev_state())
        self.push_command_result(ResultCode.OK, "On")
        return [ResultCode.OK], [""]

    def is_Off_allowed(self) -> bool:
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("Off Command is allowed")
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Off(self) -> Tuple[List[ResultCode], List[str]]:
        self.update_command_info(OFF)
        if self.defective_params["enabled"]:
            return self.induce_fault(
                "Off",
            )

        self.set_state(DevState.OFF)
        self.push_change_event("State", self.dev_state())
        self.push_command_result(ResultCode.OK, "Off")
        return [ResultCode.OK], [""]

    def is_Standby_allowed(self) -> bool:
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("Standby Command is allowed")
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Standby(self) -> Tuple[List[ResultCode], List[str]]:
        self.update_command_info(STAND_BY)
        if self.defective_params["enabled"]:
            return self.induce_fault(
                "Standby",
            )

        self.set_state(DevState.STANDBY)
        self.push_change_event("State", self.dev_state())
        self.push_command_result(ResultCode.OK, "Standby")
        return [ResultCode.OK], [""]

    def is_AssignResources_allowed(self) -> bool:
        """
        This method checks if the AssignResources command is allowed or not
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("AssignResources Command is allowed")
        return True

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format consists of receptorIDList.",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def AssignResources(
        self, argin: str = ""
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This is the method to invoke AssignResources command.
        :return: ResultCode, message
        :rtype: tuple
        """
        self.update_command_info(ASSIGN_RESOURCES, argin)
        if self.defective_params["enabled"]:
            return self.induce_fault(
                "AssignResources",
            )

        if self._state_duration_info:
            self._follow_state_duration()
        else:
            self._obs_state = ObsState.RESOURCING
            self.push_obs_state_event(self._obs_state)
            thread = threading.Timer(
                self._delay, self.update_device_obsstate, args=[ObsState.IDLE]
            )
            thread.start()
            self.push_command_result(ResultCode.OK, "AssignResources")
            self.logger.debug(
                "AssignResources command invoked, obsState will transition to"
                + "IDLE, current obsState is %s",
                self._obs_state,
            )
        return [ResultCode.OK], [""]

    def is_Configure_allowed(self) -> bool:
        """
        This method checks the Configure is allowed in the current device
        state.
        :rtype:bool
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("Configure Command is allowed")
        return True

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Configure(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        This is the method to invoke Configure command.
        :return: ResultCode, message
        :rtype: tuple
        """
        self.update_command_info(CONFIGURE, argin)
        if self.defective_params["enabled"]:
            return self.induce_fault(
                "Configure",
            )
        if self._state_duration_info:
            self._follow_state_duration()
        else:
            self._obs_state = ObsState.CONFIGURING
            self.push_obs_state_event(self._obs_state)
            thread = threading.Timer(
                self._delay, self.update_device_obsstate, args=[ObsState.READY]
            )
            thread.start()
            self.push_command_result(ResultCode.OK, "Configure")
            self.logger.debug(
                "Configure command invoked, obsState will transition to"
                + "READY, current obsState is %s",
                self._obs_state,
            )
        return [ResultCode.OK], [""]

    def is_Scan_allowed(self) -> bool:
        """
        This method checks if the Scan command is allowed in the current
        device state.
        :rtype:bool
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("Scan Command is allowed")
        return True

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Scan(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        This is the method to invoke Scan command.
        :return: ResultCode, message
        :rtype: tuple
        """
        self.update_command_info(SCAN, argin)
        if self.defective_params["enabled"]:
            return self.induce_fault(
                "Scan",
            )

        self._obs_state = ObsState.SCANNING
        self.push_obs_state_event(self._obs_state)
        self.push_command_result(ResultCode.OK, "Scan")
        self.logger.info("Scan command completed.")
        return [ResultCode.OK], [""]

    def is_EndScan_allowed(self) -> bool:
        """
        This method checks if the EndScan command is allowed in the current
        device state.
        :rtype:bool
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("EndScan Command is allowed")
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def EndScan(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This is the method to invoke EndScan command.
        :return: ResultCode, message
        :rtype: tuple
        """
        self.update_command_info(END_SCAN)
        if self.defective_params["enabled"]:
            return self.induce_fault(
                "EndScan",
            )

        self._obs_state = ObsState.READY
        self.push_obs_state_event(self._obs_state)
        self.push_command_result(ResultCode.OK, "EndScan")
        self.logger.info("EndScan command completed.")
        return [ResultCode.OK], [""]

    def is_End_allowed(self) -> bool:
        """
        This method checks if the End command is allowed in the current
        device state.
        :rtype:bool
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("End Command is allowed")
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def End(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This is the method to invoke End command.
        :return: ResultCode, message
        :rtype: tuple
        """
        self.update_command_info(END)
        if self.defective_params["enabled"]:
            return self.induce_fault(
                "End",
            )

        self._obs_state = ObsState.CONFIGURING
        self.push_obs_state_event(self._obs_state)
        thread = threading.Timer(
            self._delay, self.update_device_obsstate, args=[ObsState.IDLE]
        )
        thread.start()
        self.push_command_result(ResultCode.OK, "End")
        self.logger.debug(
            "End command invoked, obsState will transition to"
            + "IDLE, current obsState is %s",
            self._obs_state,
        )
        return [ResultCode.OK], [""]

    def is_GoToIdle_allowed(self) -> bool:
        """
        This method checks if the GoToIdle command is allowed in the current
        device state.
        :rtype:bool
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("GoToIdle Command is allowed")
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def GoToIdle(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This is the method to invoke GoToIdle command.
        :return: ResultCode, message
        :rtype: tuple
        """
        self.update_command_info(GO_TO_IDLE)
        if self.defective_params["enabled"]:
            return self.induce_fault(
                "GoToIdle",
            )

        self._obs_state = ObsState.IDLE
        self.push_obs_state_event(self._obs_state)
        self.push_command_result(ResultCode.OK, "GoToIdle")
        return [ResultCode.OK], [""]

    def is_Abort_allowed(self) -> bool:
        """
        This method checks if the Abort command is allowed in the current
        device state.
        :rtype:bool
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("Abort Command is allowed")
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Abort(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This is the method to invoke Abort command.
        :return: ResultCode, message
        :rtype: tuple
        """
        self.update_command_info(ABORT)
        if self.defective_params["enabled"]:
            return self.induce_fault(
                "Abort",
            )

        self._obs_state = ObsState.ABORTING
        self.push_obs_state_event(self._obs_state)
        thread = threading.Timer(
            self._delay, self.update_device_obsstate, args=[ObsState.ABORTED]
        )
        thread.start()
        self.push_command_result(ResultCode.OK, "Abort")
        self.logger.debug(
            "Abort command invoked, obsState will transition to"
            + "ABORTED, current obsState is %s",
            self._obs_state,
        )
        return [ResultCode.OK], [""]

    def is_Restart_allowed(self) -> bool:
        """
        This method checks if the Restart command is allowed in the current
        device state.
        :rtype:bool
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("Restart Command is allowed")
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Restart(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This is the method to invoke Restart command.
        :return: ResultCode, message
        :rtype: tuple
        """
        self.update_command_info(RESTART)
        if self.defective_params["enabled"]:
            return self.induce_fault(
                "Restart",
            )

        self._obs_state = ObsState.RESTARTING
        self.push_obs_state_event(self._obs_state)
        thread = threading.Timer(
            self._delay, self.update_device_obsstate, args=[ObsState.EMPTY]
        )
        thread.start()
        self.push_command_result(ResultCode.OK, "Restart")
        self.logger.info("Restart command completed.")
        return [ResultCode.OK], [""]

    def is_ReleaseAllResources_allowed(self) -> bool:
        """
        This method checks if the ReleaseAllResources command is allowed in
        the current device state.
        :return: ResultCode, message
        :rtype: tuple
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("ReleaseAllResources Command is allowed")
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ReleaseAllResources(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This is the method to invoke ReleaseAllResources command.
        :return: ResultCode, message
        :rtype: tuple
        """
        self.update_command_info(RELEASE_ALL_RESOURCES)
        if self.defective_params["enabled"]:
            return self.induce_fault(
                "ReleaseAllResources",
            )

        self._obs_state = ObsState.RESOURCING
        self.push_obs_state_event(self._obs_state)
        thread = threading.Timer(
            self._delay, self.update_device_obsstate, args=[ObsState.EMPTY]
        )
        thread.start()
        self.push_command_result(ResultCode.OK, "ReleaseAllResources")
        self.logger.debug(
            "ReleaseAllResources command invoked, obsState will transition to"
            + "EMPTY, current obsState is %s",
            self._obs_state,
        )
        return [ResultCode.OK], [""]

    def is_ReleaseResources_allowed(self) -> bool:
        """
        This method checks if the ReleaseResources command is allowed in the
        current device state.
        :return: ResultCode, message
        :rtype: tuple
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("ReleaseResources Command is allowed")
        return True

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format consists of receptorIDList.",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ReleaseResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This is the method to invoke ReleaseResources command.
        :return: ResultCode, message
        :rtype: tuple
        """
        self.update_command_info(RELEASE_RESOURCES)
        if self.defective_params["enabled"]:
            return self.induce_fault(
                "ReleaseResources",
            )

        self._obs_state = ObsState.RESOURCING
        self.push_obs_state_event(self._obs_state)
        thread = threading.Timer(
            self._delay, self.update_device_obsstate, args=[ObsState.IDLE]
        )
        thread.start()
        self.push_command_result(ResultCode.OK, "ReleaseResources")
        self.logger.debug(
            "ReleaseResources command invoked, obsState will transition to"
            + "IDLE, current obsState is %s",
            self._obs_state,
        )
        return [ResultCode.OK], [""]


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """
    Runs the HelperSubarrayLeafDevice Tango device.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: integer. Exit code of the run method.
    """
    return run((HelperSubarrayLeafDevice,), args=args, **kwargs)


if __name__ == "__main__":
    main()
