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
from tango.server import AttrWriteType, attribute, command, run

from ska_tmc_common import CommandNotAllowed, FaultType
from ska_tmc_common.admin_mode_decorator import admin_mode_check
from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice

from .constants import (
    ABORT,
    ASSIGN_RESOURCES,
    CONFIGURE,
    END,
    END_SCAN,
    GO_TO_IDLE,
    RELEASE_ALL_RESOURCES,
    RELEASE_RESOURCES,
    RESTART,
    SCAN,
)


# pylint: disable=invalid-name
class HelperSubarrayLeafDevice(HelperBaseDevice):
    """A device exposing commands and attributes of the Subarray Leaf Nodes
    devices."""

    def init_device(self) -> None:
        super().init_device()
        self._obs_state = ObsState.EMPTY
        self._state_duration_info = []
        # list of tuple
        self._command_call_info = []
        self._command_info = ("", "")
        self._isAdminModeEnabled: bool = True

    class InitCommand(HelperBaseDevice.InitCommand):
        """A class for the HelperSubarrayDevice's init_device() "command"."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            :return: ResultCode and message
            """
            super().do()
            self._device.set_change_event("obsState", True, False)
            self._device.set_change_event("commandCallInfo", True, False)
            self._device.op_state_model.perform_action("component_on")
            return ResultCode.OK, ""

    defective = attribute(dtype=str, access=AttrWriteType.READ)

    obsState = attribute(dtype=ObsState, access=AttrWriteType.READ)

    isSubsystemAvailable = attribute(dtype=bool, access=AttrWriteType.READ)

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
        """
        Read transition
        :return: state duration info
        """
        return json.dumps(self._state_duration_info)

    def read_commandCallInfo(self):
        """
        This method is used to read the attribute value for
        commandCallInfo.
        :return: attribute value for commandCallInfo
        """
        return self._command_call_info

    def read_defective(self) -> str:
        """
        Returns defective status of devices
        :return: attribute value defective
        :rtype: str
        """
        return json.dumps(self.defective_params)

    def read_obsState(self) -> ObsState:
        """
        This method is used to read the attribute value for obsState.
        :return: attribute value for obsstate
        """
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
        self._command_info = (command_name, command_input)
        self._command_call_info.append(self._command_info)
        self.logger.info(
            "Recorded command_call_info list for: %s is %s",
            self.dev_name,
            self._command_call_info,
        )
        self.push_change_event("commandCallInfo", self._command_call_info)

    def _follow_state_duration(self):
        """This method will update obs state as per state duration
        in separate thread.
        To avoid Tango default 3 sec timeout creating seperate thread
        for updating obs state.As Updating Obs state might take
        more than 3 sec.
        """
        for obs_state, duration in self._state_duration_info:
            obs_state = ObsState[obs_state]
            time.sleep(duration)
            thread = threading.Thread(
                target=self.push_obs_state_event,
                args=[obs_state],
            )
            thread.start()

    @command(
        doc_in="Clears commandCallInfo",
    )
    def ClearCommandCallInfo(self) -> None:
        """Clears commandCallInfo to empty list"""
        self.logger.info("Clearing CommandCallInfo for %s", self.dev_name)
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
            "ObsState transitions sequence for %s is: %s",
            self.dev_name,
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

    def push_obs_state_event(self, obs_state: ObsState) -> None:
        """Push Obs State Change Event"""
        with tango.EnsureOmniThread():
            self.logger.info(
                "Pushing change event for %s: %s",
                self.dev_name,
                obs_state,
            )
            self._obs_state = obs_state
            self.push_change_event("obsState", self._obs_state)

    @admin_mode_check()
    def is_AssignResources_allowed(self) -> bool:
        """
        This method checks if the AssignResources command is allowed or not
        :return: ``True`` if the command is allowed
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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
        command_id = f"{time.time()}_AssignResources"
        self.update_command_info(ASSIGN_RESOURCES, argin)
        if self.defective_params["enabled"]:
            return self.induce_fault(
                "AssignResources",
                command_id,
            )

        if self._state_duration_info:
            self._follow_state_duration()
        else:
            self.push_obs_state_event(ObsState.RESOURCING)
            thread = threading.Timer(
                self._delay, self.push_obs_state_event, args=[ObsState.IDLE]
            )
            thread.start()
            result_thread = threading.Timer(
                self._delay,
                function=self.push_command_result,
                args=[ResultCode.OK, "AssignResources"],
                kwargs={"command_id": command_id},
            )
            result_thread.start()
            self.logger.debug(
                "AssignResources command invoked, obsState will transition to"
                + "IDLE, current obsState is %s",
                self._obs_state,
            )
        return [ResultCode.QUEUED], [command_id]

    @admin_mode_check()
    def is_Configure_allowed(self) -> bool:
        """
        This method checks the Configure is allowed in the current device
        state.
        :return: ``True`` if the command is allowed
        :rtype:bool
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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
        command_id = f"{time.time()}_Configure"
        self.update_command_info(CONFIGURE, argin)
        if self.defective_params["enabled"]:
            return self.induce_fault("Configure", command_id)
        if self._state_duration_info:
            self._follow_state_duration()
        else:
            self.push_obs_state_event(ObsState.CONFIGURING)
            thread = threading.Timer(
                self._delay, self.push_obs_state_event, args=[ObsState.READY]
            )
            thread.start()
            result_thread = threading.Timer(
                self._delay,
                function=self.push_command_result,
                args=[
                    ResultCode.OK,
                    "Configure",
                ],
                kwargs={"command_id": command_id},
            )
            result_thread.start()
            self.logger.info(
                "Configure command invoked, obsState will transition to"
                + "READY, current obsState is %s",
                self._obs_state,
            )
        return [ResultCode.QUEUED], [command_id]

    @admin_mode_check()
    def is_Scan_allowed(self) -> bool:
        """
        This method checks if the Scan command is allowed in the current
        device state.
        :return: ``True`` if the command is allowed
        :rtype:bool
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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
        command_id = f"{time.time()}_Scan"
        self.update_command_info(SCAN, argin)
        if self.defective_params["enabled"]:
            return self.induce_fault("Scan", command_id)

        self.push_obs_state_event(ObsState.SCANNING)

        thread = threading.Timer(
            self._delay,
            self.push_command_result,
            args=[ResultCode.OK, "Scan"],
            kwargs={"command_id": command_id},
        )
        thread.start()
        self.logger.info("Scan command completed.")

        return [ResultCode.QUEUED], [command_id]

    @admin_mode_check()
    def is_EndScan_allowed(self) -> bool:
        """
        This method checks if the EndScan command is allowed in the current
        device state.
        :return: ``True`` if the command is allowed
        :rtype:bool
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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
        command_id = f"{time.time()}_EndScan"
        self.update_command_info(END_SCAN)
        if self.defective_params["enabled"]:
            return self.induce_fault("EndScan", command_id)

        self.push_obs_state_event(ObsState.READY)
        self.push_command_result(
            ResultCode.OK, "EndScan", command_id=command_id
        )
        self.logger.info("EndScan command completed.")
        return [ResultCode.QUEUED], [command_id]

    @admin_mode_check()
    def is_End_allowed(self) -> bool:
        """
        This method checks if the End command is allowed in the current
        device state.
        :return: ``True`` if the command is allowed
        :rtype:bool
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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
        command_id = f"{time.time()}_End"
        self.update_command_info(END)
        if self.defective_params["enabled"]:
            return self.induce_fault("End", command_id)

        self.push_obs_state_event(ObsState.IDLE)
        self.push_command_result(ResultCode.OK, "End", command_id=command_id)
        self.logger.debug(
            "End command invoked, obsState will transition to"
            + "IDLE, current obsState is %s",
            self._obs_state,
        )
        return [ResultCode.QUEUED], [command_id]

    @admin_mode_check()
    def is_GoToIdle_allowed(self) -> bool:
        """
        This method checks if the GoToIdle command is allowed in the current
        device state.
        :return: ``True`` if the command is allowed
        :rtype:bool
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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
        command_id = f"{time.time()}_GoToIdle"
        self.update_command_info(GO_TO_IDLE)
        if self.defective_params["enabled"]:
            return self.induce_fault("GoToIdle", command_id)

        self._obs_state = ObsState.IDLE
        self.push_obs_state_event(self._obs_state)
        self.push_command_result(ResultCode.OK, "GoToIdle")
        return [ResultCode.QUEUED], [command_id]

    @admin_mode_check()
    def is_Abort_allowed(self) -> bool:
        """
        This method checks if the Abort command is allowed in the current
        device state.
        :return: ``True`` if the command is allowed
        :rtype:bool
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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
        command_id = f"{time.time()}_Abort"
        self.update_command_info(ABORT)
        if self.defective_params["enabled"]:
            return self.induce_fault("Abort", command_id)

        self.push_obs_state_event(ObsState.ABORTING)
        thread = threading.Timer(
            self._delay, self.push_obs_state_event, args=[ObsState.ABORTED]
        )
        thread.start()
        thread = threading.Timer(
            self._delay,
            self.push_command_result,
            args=[ResultCode.OK, "Abort"],
            kwargs={"command_id": command_id},
        )
        thread.start()
        self.logger.debug(
            "Abort command invoked, obsState will transition to"
            + "ABORTED, current obsState is %s",
            self._obs_state,
        )
        return [ResultCode.QUEUED], [command_id]

    @admin_mode_check()
    def is_Restart_allowed(self) -> bool:
        """
        This method checks if the Restart command is allowed in the current
        device state.
        :return: ``True`` if the command is allowed
        :rtype:bool
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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
        command_id = f"{time.time()}_Restart"
        self.update_command_info(RESTART)
        if self.defective_params["enabled"]:
            return self.induce_fault("Restart", command_id)

        self.push_obs_state_event(ObsState.RESTARTING)
        thread = threading.Timer(
            self._delay, self.push_obs_state_event, args=[ObsState.EMPTY]
        )
        thread.start()
        thread = threading.Timer(
            self._delay,
            self.push_command_result,
            args=[ResultCode.OK, "Restart"],
            kwargs={"command_id": command_id},
        )
        thread.start()
        self.logger.info("Restart command completed.")
        return [ResultCode.QUEUED], [command_id]

    @admin_mode_check()
    def is_ReleaseAllResources_allowed(self) -> bool:
        """
        This method checks if the ReleaseAllResources command is allowed in
        the current device state.
        :return: ``True`` if the command is allowed
        :raises CommandNotAllowed: command is not allowed
        :rtype: bool
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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
        command_id = f"{time.time()}_ReleaseAllResources"
        self.update_command_info(RELEASE_ALL_RESOURCES)
        if self.defective_params["enabled"]:
            return self.induce_fault("ReleaseAllResources", command_id)

        self.push_obs_state_event(ObsState.RESOURCING)
        thread = threading.Timer(
            self._delay, self.push_obs_state_event, args=[ObsState.EMPTY]
        )
        thread.start()
        thread = threading.Timer(
            self._delay,
            self.push_command_result,
            args=[ResultCode.OK, "ReleaseAllResources"],
            kwargs={"command_id": command_id},
        )
        thread.start()
        self.logger.debug(
            "ReleaseAllResources command invoked, obsState will transition to"
            + "EMPTY, current obsState is %s",
            self._obs_state,
        )
        return [ResultCode.QUEUED], [command_id]

    @admin_mode_check()
    def is_ReleaseResources_allowed(self) -> bool:
        """
        This method checks if the ReleaseResources command is allowed in the
        current device state.
        :return: ``True`` if the command is allowed
        :raises CommandNotAllowed: command is not allowed
        :rtype: bool
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
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
        command_id = f"{time.time()}_ReleaseResources"
        self.update_command_info(RELEASE_RESOURCES)
        if self.defective_params["enabled"]:
            return self.induce_fault("ReleaseResources", command_id)

        self.push_obs_state_event(ObsState.RESOURCING)
        thread = threading.Timer(
            self._delay, self.push_obs_state_event, args=[ObsState.IDLE]
        )
        thread.start()
        thread = threading.Timer(
            self._delay,
            self.push_command_result,
            args=[ResultCode.OK, "ReleaseResources"],
            kwargs={"command_id": command_id},
        )
        thread.start()
        self.logger.debug(
            "ReleaseResources command invoked, obsState will transition to"
            + "IDLE, current obsState is %s",
            self._obs_state,
        )
        return [ResultCode.QUEUED], [command_id]


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
