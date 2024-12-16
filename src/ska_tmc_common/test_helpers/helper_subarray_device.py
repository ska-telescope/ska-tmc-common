# pylint: disable=too-many-lines
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
from tango import AttrWriteType, DevState
from tango.server import attribute, command, run

from ska_tmc_common import CommandNotAllowed, FaultType
from ska_tmc_common.test_helpers.constants import (
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


# pylint: disable=abstract-method,invalid-name
# Disabled as this is also a abstract class and has parent class from
# base class.
# Disabled invalid-name as this is tango device class
class EmptySubArrayComponentManager(SubarrayComponentManager):
    """
    This is a Component Manager created for the use of Helper Subarray devices.
    """

    # pylint: disable=arguments-renamed
    # The pylint error arguments-renamed is disabled becasue base class has
    # second parameter as task_callback which is not used here
    def __init__(
        self,
        logger: Logger,
        communication_state_callback: Optional[Callable] = None,
        component_state_callback: Optional[Callable] = None,
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
        :return: ResultCode, message
        :rtype:tuple
        """
        self.logger.info("Resources: %s", resources)
        self._assigned_resources = ["0001"]
        return ResultCode.OK, ""

    def release(self, resources: list) -> Tuple[ResultCode, str]:
        """
        Release resources from the component.
        :param resources: resources to be released
        :return: ResultCode, message
        :rtype:tuple
        """
        self.logger.info("Released Resources: %s", resources)
        return ResultCode.OK, ""

    def release_all(self) -> Tuple[ResultCode, str]:
        """
        Release all resources.
        :return: ResultCode, message
        :rtype:tuple
        """
        self._assigned_resources = []

        return ResultCode.OK, ""

    def configure(self, configuration: str) -> Tuple[ResultCode, str]:
        """
        Configure the component.
        :param configuration: the configuration to be configured
        :type configuration: str
        :return: ResultCode, message
        :rtype:tuple
        """
        self.logger.info("%s", configuration)

        return ResultCode.OK, ""

    def scan(self, args: Any) -> Tuple[ResultCode, str]:
        """
        Start scanning.
        :return: ResultCode, message
        :rtype:tuple
        """
        self.logger.info("%s", args)
        return ResultCode.OK, ""

    def end_scan(self) -> Tuple[ResultCode, str]:
        """
        End scanning.
        :return: ResultCode, message
        :rtype:tuple
        """

        return ResultCode.OK, ""

    def end(self) -> Tuple[ResultCode, str]:
        """
        End Scheduling blocks.
        :return: ResultCode, message
        :rtype:tuple
        """

        return ResultCode.OK, ""

    def abort(self) -> Tuple[ResultCode, str]:
        """
        Tell the component to abort whatever it was doing.
        :return: ResultCode, message
        :rtype:tuple
        """

        return ResultCode.OK, ""

    def obsreset(self) -> Tuple[ResultCode, str]:
        """
        Reset the component to unconfirmed but do not release resources.
        :return: ResultCode, message
        :rtype:tuple
        """

        return ResultCode.OK, ""

    def restart(self) -> Tuple[ResultCode, str]:
        """
        Deconfigure and release all resources.
        :return: ResultCode, message
        :rtype:tuple
        """

        return ResultCode.OK, ""

    @property
    def assigned_resources(self) -> list:
        """
        Return the resources assigned to the component.

        :return: the resources assigned to the component
        :rtype: list
        """
        # import debugpy; debugpy.debug_this_thread()
        return self._assigned_resources


# pylint: disable=too-many-instance-attributes
class HelperSubArrayDevice(SKASubarray):
    """A generic subarray device for triggering state changes with a command.
    It can be used as helper device for element subarray node"""

    def init_device(self):
        super().init_device()
        self._health_state = HealthState.OK
        self._isSubsystemAvailable = True
        self._command_in_progress = ""
        self._command_delay_info = {
            ASSIGN_RESOURCES: 2,
            CONFIGURE: 2,
            RELEASE_RESOURCES: 2,
            ABORT: 2,
            RESTART: 2,
            RELEASE_ALL_RESOURCES: 2,
            END: 2,
        }
        self.dev_name = self.get_name()
        self._scan_id = 0
        self._assigned_resources = "{ }"
        # tuple of list
        self._command_call_info = []
        self._command_info = ("", "")
        self._state_duration_info = []
        self._delay = 2
        self.defective_params = {
            "enabled": False,
            "fault_type": FaultType.FAILED_RESULT,
            "error_message": "Default exception.",
            "result": ResultCode.FAILED,
        }
        self._receive_addresses = ""

    class InitCommand(SKASubarray.InitCommand):
        """A class for the HelperSubarrayDevice's init_device() "command"."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialization.
            :return: ResultCode
            """
            super().do()
            self._device.set_change_event("obsState", True, False)
            self._device.set_change_event("commandInProgress", True, False)
            self._device.set_change_event("commandCallInfo", True, False)
            self._device.set_change_event("assignedResources", True, False)
            self._device.set_change_event("isSubsystemAvailable", True, False)
            return ResultCode.OK, ""

    commandInProgress = attribute(dtype="DevString", access=AttrWriteType.READ)

    receiveAddresses = attribute(dtype="DevString", access=AttrWriteType.READ)

    defective = attribute(dtype=str, access=AttrWriteType.READ)

    commandDelayInfo = attribute(dtype=str, access=AttrWriteType.READ)

    commandCallInfo = attribute(
        dtype=(("str",),),
        access=AttrWriteType.READ,
        max_dim_x=100,
        max_dim_y=100,
    )

    obsStateTransitionDuration = attribute(
        dtype="DevString", access=AttrWriteType.READ
    )

    scanId = attribute(dtype="DevLong", access=AttrWriteType.READ)

    isSubsystemAvailable = attribute(dtype=bool, access=AttrWriteType.READ)

    @attribute(dtype=("DevString"), max_dim_x=1024)
    def assignedResources(self) -> str:
        return self._assigned_resources

    def read_scanId(self) -> int:
        """
        This method is used to read the attribute value for scanId.
        :return: scan_id
        """
        return self._scan_id

    def read_obsStateTransitionDuration(self):
        """
        Read transition
        :return: state dureation info
        """
        return json.dumps(self._state_duration_info)

    def read_isSubsystemAvailable(self) -> bool:
        """
        Returns avalability status for the leaf nodes devices
        :return: avalability status for the leaf nodes devices
        :rtype: bool
        """
        return self._isSubsystemAvailable

    @command(
        dtype_in=bool,
        doc_in="Set Availability of the device",
    )
    def SetSubsystemAvailable(self, value: bool) -> None:
        """
        Sets Availability of the device
        :rtype: bool
        """
        self.logger.info("Setting the avalability value to : %s", value)
        if self._isSubsystemAvailable != value:
            self._isSubsystemAvailable = value
            self.push_change_event(
                "isSubsystemAvailable", self._isSubsystemAvailable
            )

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
            "ObsState transitions sequence for %s simulator is: %s",
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

    def read_commandCallInfo(self):
        """
        This method is used to read the attribute value for
        commandCallInfo.
        :return: attribute value for commandCallInfo
        """
        return self._command_call_info

    def read_commandDelayInfo(self):
        """
        This method is used to read the attribute value for delay.
        :return: attribute value for delay
        """

        return json.dumps(self._command_delay_info)

    def read_commandInProgress(self) -> str:
        """
        This method is used to read, which command is in progress
        :return: command in progress
        :rtype:str
        """
        return self._command_in_progress

    def read_defective(self) -> str:
        """
        This method is used to read the value of the attribute defective
        :return: attribute value defective
        :rtype: str
        """
        return json.dumps(self.defective_params)

    def read_receiveAddresses(self) -> str:
        """
        This method is used to read receiveAddresses attribute
        :return: attribute receiveAddresses
        :rtype:str
        """
        return self._receive_addresses

    def push_command_result(
        self,
        result_code: ResultCode,
        command_name: str,
        message: str = "Command Completed",
        command_id: str = "",
    ) -> None:
        """
        Push long running command result event for given command.

        :param result_code: The result code to be pushed as an event
        :type result_code: ResultCode
        :param command_name: The command name for which event is being pushed
        :type command_name: str
        :param message: The message associated with the command result
        :type message: str
        :param command_id: The unique command id
        :type command_id: str
        """

        if not command_id:
            command_id = f"{time.time()}-{command_name}"
        command_result = (
            command_id,
            json.dumps((result_code, message)),
        )
        self.logger.info(
            "Pushing longRunningCommandResult Event with data: %s",
            command_result,
        )
        self.push_change_event("longRunningCommandResult", command_result)

    def update_device_obsstate(
        self, value: ObsState, command_name: str = ""
    ) -> None:
        """Updates the given data after a delay."""
        with tango.EnsureOmniThread():
            # If the current obsState is ABORTING or ABORTED, don't push events
            # other than ObsState.ABORTED or ObsState.RESTARTING. This is to
            # avoid cases where abort is invoked on a device and it still sends
            # out other ObsState events.
            if self._obs_state not in [
                ObsState.ABORTING,
                ObsState.ABORTED,
            ] or value in [ObsState.ABORTED, ObsState.RESTARTING]:
                self.logger.info(
                    "Pushing ObsState event for command: %s and obsState: %s",
                    command_name,
                    value,
                )
                self._obs_state = value
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
        self._command_info = (command_name, command_input)
        self._command_call_info.append(self._command_info)
        self.logger.info(
            "Recorded command_call_info list for %s is %s",
            self.dev_name,
            self._command_call_info,
        )

        self.push_change_event("commandCallInfo", self._command_call_info)
        self.logger.info("CommandCallInfo updates are pushed")

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

    def create_component_manager(self) -> EmptySubArrayComponentManager:
        """
        This method is used to create an instance of
        EmptySubarrayComponentManager
        :return: component manager
        :rtype: EmptySubArrayComponentManager
        """
        cm = EmptySubArrayComponentManager(
            logger=self.logger,
            communication_state_callback=None,
            component_state_callback=None,
        )
        return cm

    @command(
        dtype_in=str,
        doc_in="Set Delay",
    )
    def SetDelayInfo(self, command_delay_info: str) -> None:
        """Update delay value"""
        self.logger.info(
            "Setting the Delay value for %s to : %s",
            self.dev_name,
            command_delay_info,
        )
        # set command info
        command_delay_info_dict = json.loads(command_delay_info)
        for key, value in command_delay_info_dict.items():
            self._command_delay_info[key] = value

    @command(
        doc_in="Reset Delay",
    )
    def ResetDelayInfo(self) -> None:
        """Reset Delay to it's default values"""
        self.logger.info(
            "Resetting Command Delays for %s",
            self.dev_name,
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
            "Clearing CommandCallInfo for %s",
            self.dev_name,
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
            self.logger.info("Device obsState is set to %s", self._obs_state)

    @command(
        dtype_in="DevState",
        doc_in="state to assign",
    )
    def SetDirectState(self, argin: tango.DevState) -> None:
        """
        Trigger a DevState if self.dev_state() != argin:
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

    @command(
        dtype_in=("DevString"),
        doc_in="assignedResources attribute value",
    )
    def SetDirectassignedResources(self, argin: str) -> None:
        """
        Triggers an assignedResources attribute change.
        Note: This method should be used only in case of low.
        """
        if self._assigned_resources != argin:
            self._assigned_resources = argin
            self.push_change_event("assignedResources", argin)
            self.logger.info(
                "Updated assignedResources attribute value to %s", str(argin)
            )

    def is_On_allowed(self) -> bool:
        """
        Check if command `On` is allowed in the current device
        state.

        :return: ``True`` if the command is allowed
        :rtype: bool
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
        self.logger.info("On command is allowed")
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def On(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes On command on Subarray Device
        :return: ResultCode
        :rtype: Tuple
        """
        command_id = f"{time.time()}_On"
        self.logger.info("Instructed simulator to invoke On command")
        self.update_command_info(ON, "")
        if self.defective_params["enabled"]:
            return self.induce_fault("On", command_id)
        if self.dev_state() != DevState.ON:
            self.set_state(DevState.ON)
            self.push_change_event("State", self.dev_state())
            self.logger.info("On command completed.")
        return [ResultCode.QUEUED], [command_id]

    def is_Off_allowed(self) -> bool:
        """
        Check if command `Off` is allowed in the current device
        state.

        :return: ``True`` if the command is allowed
        :rtype: bool
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
        self.logger.info("Off command is allowed")
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Off(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes Off command on Subarray Device
        :return: ResultCode and message
        :rtype: Tuple
        """
        command_id = f"{time.time()}_Off"
        self.logger.info("Instructed simulator to invoke Off command")
        self.update_command_info(OFF, "")
        if self.defective_params["enabled"]:
            return self.induce_fault("Off", command_id)
        if self.dev_state() != DevState.OFF:
            self.set_state(DevState.OFF)
            self.push_change_event("State", self.dev_state())
            self.logger.info("Off completed")
        return [ResultCode.QUEUED], [command_id]

    def induce_fault(
        self,
        command_name: str,
        command_id: str,
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        Induces a fault into the device based on the given parameters.

        :param command_name: The name of the command for which a fault is
            being induced.
        :type command_name: str
        :param command_id: The command id over which the LRCR event is to be
            pushed.
        :type command_id: str

        :return: ResultCode and Unique_ID
        :rtype: Tuple[List[ResultCode], List[str]]

        Example:
            defective_params = json.dumps({"enabled": False,"fault_type":
            FaultType.FAILED_RESULT,"error_message": "Default exception.",
            "result": ResultCode.FAILED,})
            proxy.SetDefective(defective_params)

        Explanation:
        This method induces various types of faults into a device to test its
        robustness and error-handling capabilities.

        - FAILED_RESULT:
            A fault type that triggers a failed result code
            for the command. The device will return a result code of 'FAILED'
            along with a unique_id indicating that the command execution has
            failed.

        - LONG_RUNNING_EXCEPTION:
            A fault type where a failed result will be sent over the
            LongRunningCommandResult attribute in 'delay' amount of time.

        - STUCK_IN_INTERMEDIATE_STATE:
            This fault type makes it such that the device is stuck in the given
            Observation state.

        - COMMAND_NOT_ALLOWED_AFTER_QUEUING:
            This fault type sends a ResultCode.NOT_ALLOWED event through the
            LongRunningCommandResult attribute.

        - COMMAND_NOT_ALLOWED_EXCEPTION_AFTER_QUEUING:
            This fault type sends a ResultCode.REJECTED event through the
            LongRunningCommandResult attribute.

        - STUCK_IN_OBS_STATE:
            This fault type sets the device to given obsState and sends out an
            event on the LongRunningCommandResult attribute.

        """
        self.logger.info("Inducing fault for command %s", command_name)
        fault_type = self.defective_params.get("fault_type")
        result = self.defective_params.get("result", ResultCode.FAILED)
        fault_message = self.defective_params.get(
            "error_message", "Exception occurred"
        )
        intermediate_state = (
            self.defective_params.get("intermediate_state")
            or ObsState.RESOURCING
        )

        if fault_type == FaultType.FAILED_RESULT:
            if "target_obsstates" in self.defective_params:
                # Utilise target_obsstate parameter when Subarray should
                # transition to specific obsState while returning
                # ResultCode.FAILED
                obsstate_list = self.defective_params["target_obsstates"]
                for obsstate in obsstate_list:
                    self._obs_state = obsstate
                    self.logger.info(
                        "pushing target obsstate %s event", self._obs_state
                    )
                    self.push_change_event("obsState", self._obs_state)

                command_result = (
                    command_id,
                    json.dumps(
                        (
                            ResultCode.FAILED,
                            f"Exception occured on device: {self.get_name()}",
                        )
                    ),
                )
                self.logger.info(
                    "pushing longRunningCommandResult %s event", command_result
                )
                self.push_change_event(
                    "longRunningCommandResult", command_result
                )
            return [result], [command_id]

        if fault_type == FaultType.LONG_RUNNING_EXCEPTION:
            thread = threading.Timer(
                self._delay,
                function=self.push_command_result,
                args=[result, command_name],
                kwargs={"message": fault_message, "command_id": command_id},
            )
            thread.start()
            return [ResultCode.QUEUED], [command_id]

        if fault_type == FaultType.STUCK_IN_INTERMEDIATE_STATE:
            self._obs_state = intermediate_state
            self.push_change_event("obsState", intermediate_state)
            return [ResultCode.QUEUED], [command_id]

        if fault_type == FaultType.COMMAND_NOT_ALLOWED_AFTER_QUEUING:
            thread = threading.Timer(
                self._delay,
                function=self.push_command_result,
                args=[
                    ResultCode.NOT_ALLOWED,
                    command_name,
                ],
                kwargs={
                    "message": "Command is not allowed",
                    "command_id": command_id,
                },
            )
            thread.start()
            return [ResultCode.QUEUED], [command_id]

        if fault_type == FaultType.STUCK_IN_OBSTATE:
            self._obs_state = intermediate_state
            self.push_change_event("obsState", intermediate_state)

            command_result = (
                command_id,
                json.dumps(
                    [
                        ResultCode.FAILED,
                        f"Exception occured on device: {self.get_name()}",
                    ]
                ),
            )
            self.logger.info(
                "pushing longRunningCommandResult %s event", command_result
            )
            self.push_change_event("longRunningCommandResult", command_result)
            return [ResultCode.QUEUED], [command_id]

        if fault_type == FaultType.COMMAND_NOT_ALLOWED_EXCEPTION_AFTER_QUEUING:
            thread = threading.Timer(
                self._delay,
                function=self.push_command_result,
                args=[
                    ResultCode.REJECTED,
                    command_name,
                ],
                kwargs={
                    "message": (
                        "Exception from 'is_cmd_allowed' method: "
                        + f"{fault_message}"
                    ),
                    "command_id": command_id,
                },
            )
            thread.start()
            return [ResultCode.QUEUED], [command_id]

        return [ResultCode.OK], [command_id]

    @command(
        dtype_in=str,
        doc_in="Set Defective parameters",
    )
    def SetDefective(self, values: str) -> None:
        """
        Trigger defective change
        :param: values
        :type: str
        """
        input_dict = json.loads(values)
        self.logger.info("Setting defective params to %s", input_dict)
        self.defective_params = input_dict

    def is_Standby_allowed(self) -> bool:
        """
        Check if command `Standby` is allowed in the current device
        state.

        :return: ``True`` if the command is allowed
        :rtype: bool
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
        self.logger.info("Standby command is allowed")
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
        command_id = f"{time.time()}_Standby"
        self.logger.info("Instructed simulator to invoke Standby command")
        self.update_command_info(STAND_BY, "")
        if self.defective_params["enabled"]:
            return self.induce_fault("Standby", command_id)

        if self.dev_state() != DevState.STANDBY:
            self.set_state(DevState.STANDBY)
            self.push_change_event("State", self.dev_state())
        self.logger.info("Standby completed")
        return [ResultCode.QUEUED], [command_id]

    def is_AssignResources_allowed(self) -> bool:
        """
        Check if command `AssignResources` is allowed in the current device
        state.

        :return: ``True`` if the command is allowed
        :rtype: bool
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
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes AssignResources command on subarray devices
        :return: ResultCode and message
        """
        command_id = f"{time.time()}_AssignResources"
        self.logger.info(
            "Instructed simulator to invoke AssignResources command"
        )
        self.update_command_info(ASSIGN_RESOURCES, argin)
        if self.defective_params["enabled"]:
            return self.induce_fault("AssignResources", command_id)

        self._obs_state = ObsState.RESOURCING
        self.push_change_event("obsState", self._obs_state)
        thread = threading.Timer(
            interval=2,
            function=self.update_device_obsstate,
            args=[ObsState.IDLE, ASSIGN_RESOURCES],
        )
        thread.start()
        self.logger.debug(
            "AssignResources command invoked, obsState will transition to"
            + "IDLE, current obsState is %s",
            self._obs_state,
        )
        return [ResultCode.QUEUED], [command_id]

    def is_ReleaseResources_allowed(self) -> bool:
        """
        Check if command `ReleaseResources` is allowed in the current device
        state.

        :return: ``True`` if the command is allowed
        :rtype: bool
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
        self.logger.info("ReleaseResources Command is allowed")
        return True

    @command(
        dtype_in="str",
        doc_in="The input string in JSON format consists of receptorIDList.",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ReleaseResources(self, argin) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes ReleaseResources command on subarray device
        :return: ResultCode and message
        """
        command_id = f"{time.time()}_ReleaseResources"
        self.logger.info(
            "Instructed simulator to invoke ReleaseResources command"
        )
        self.logger.info(argin)
        self.update_command_info(RELEASE_RESOURCES, "")
        if self.defective_params["enabled"]:
            return self.induce_fault("ReleaseResources", command_id)

        self.update_device_obsstate(ObsState.RESOURCING, RELEASE_RESOURCES)
        thread = threading.Timer(
            self._delay,
            self.update_device_obsstate,
            args=[ObsState.IDLE, RELEASE_RESOURCES],
        )
        thread.start()
        thread = threading.Timer(
            self._delay,
            self.push_command_result,
            args=[ResultCode.OK, RELEASE_RESOURCES],
            kwargs={"command_id": command_id},
        )
        thread.start()
        self.logger.debug(
            "ReleaseResources command invoked, obsState will transition to"
            + "IDLE, current obsState is %s",
            self._obs_state,
        )
        return [ResultCode.QUEUED], [command_id]

    def is_ReleaseAllResources_allowed(self) -> bool:
        """
        Check if command `ReleaseAllResources` is allowed in the current
        device state.

        :return: ``True`` if the command is allowed
        :rtype: bool
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
        self.logger.info("ReleaseAllResources command is allowed")
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
        command_id = f"{time.time()}_ReleaseAllResources"
        self.logger.info(
            "Instructed simulator to invoke ReleaseAllResources command"
        )
        self.update_command_info(RELEASE_ALL_RESOURCES, "")
        if self.defective_params["enabled"]:
            return self.induce_fault("ReleaseAllResources", command_id)

        self._obs_state = ObsState.RESOURCING
        self.push_change_event("obsState", self._obs_state)
        thread = threading.Timer(
            interval=2,
            function=self.update_device_obsstate,
            args=[ObsState.EMPTY, RELEASE_ALL_RESOURCES],
        )
        thread.start()
        thread = threading.Timer(
            self._delay,
            self.push_command_result,
            args=[ResultCode.OK, RELEASE_ALL_RESOURCES],
            kwargs={"command_id": command_id},
        )
        thread.start()
        self.logger.debug(
            "ReleaseAllResources command invoked, obsState will transition to"
            + "EMPTY, current obsState is %s",
            self._obs_state,
        )
        return [ResultCode.QUEUED], [command_id]

    def is_Configure_allowed(self) -> bool:
        """
        Check if command `Configure` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: bool
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
        command_id = f"{time.time()}_Configure"
        self.logger.info("Instructed simulator to invoke Configure command")
        self.update_command_info(CONFIGURE, argin)
        if self.defective_params["enabled"]:
            return self.induce_fault("Configure", command_id)
        if self._state_duration_info:
            self._follow_state_duration()
        else:
            self._obs_state = ObsState.CONFIGURING
            self.push_change_event("obsState", self._obs_state)
            self.logger.info("Starting Thread for configure")
            thread = threading.Timer(
                interval=self._command_delay_info[CONFIGURE],
                function=self.update_device_obsstate,
                args=[ObsState.READY, CONFIGURE],
            )
            thread.start()
            thread = threading.Timer(
                self._delay,
                self.push_command_result,
                args=[ResultCode.OK, CONFIGURE],
                kwargs={"command_id": command_id},
            )
            thread.start()
            self.logger.debug(
                "Configure command invoked, obsState will transition to"
                + "READY current obsState is %s",
                self._obs_state,
            )
        return [ResultCode.QUEUED], [command_id]

    def is_Scan_allowed(self) -> bool:
        """
        Check if command `Scan` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: bool
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
        command_id = f"{time.time()}_Scan"
        self.logger.info("Instructed simulator to invoke Scan command")
        self.update_command_info(SCAN, argin)
        if self.defective_params["enabled"]:
            return self.induce_fault("Scan", command_id)

        if self._obs_state != ObsState.SCANNING:
            self._obs_state = ObsState.SCANNING
            self.push_change_event("obsState", self._obs_state)
            thread = threading.Timer(
                self._delay,
                self.push_command_result,
                args=[ResultCode.OK, SCAN],
                kwargs={"command_id": command_id},
            )
            thread.start()
        self.logger.info("Scan command completed.")
        return [ResultCode.QUEUED], [command_id]

    def is_EndScan_allowed(self) -> bool:
        """
        Check if command `EndScan` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: bool
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
        This method invokes EndScan command on subarray devices.
        :return: ResultCode, message
        :rtype: tuple
        """
        command_id = f"{time.time()}_EndScan"
        self.logger.info("Instructed simulator to invoke EndScan command")
        self.update_command_info(END_SCAN, "")
        if self.defective_params["enabled"]:
            return self.induce_fault("EndScan", command_id)

        if self._obs_state != ObsState.READY:
            self._obs_state = ObsState.READY
            self.push_change_event("obsState", self._obs_state)
        self.logger.info("EndScan command completed.")
        return [ResultCode.QUEUED], [command_id]

    def is_End_allowed(self) -> bool:
        """
        Check if command `End` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: bool
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
        This method invokes End command on subarray devices.
        :return: ResultCode, message
        :rtype: tuple
        """
        command_id = f"{time.time()}_End"
        self.logger.info("Instructed simulator to invoke End command")
        self.update_command_info(END, "")
        if self.defective_params["enabled"]:
            return self.induce_fault("End", command_id)

        if self._obs_state != ObsState.IDLE:
            if self._state_duration_info:
                self._follow_state_duration()
            else:
                self._obs_state = ObsState.IDLE
                self.push_change_event("obsState", self._obs_state)
        self.logger.info("End command completed.")
        return [ResultCode.QUEUED], [command_id]

    def is_GoToIdle_allowed(self) -> bool:
        """
        Check if command `GoToIdle` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: bool
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
        This method invokes GoToIdle command on subarray devices.
        :return: ResultCode, message
        :rtype: tuple
        """
        command_id = f"{time.time()}_GoToIdle"
        self.logger.info("Instructed simulator to invoke GoToIdle command")
        self.update_command_info(GO_TO_IDLE, "")
        if self.defective_params["enabled"]:
            return self.induce_fault("GoToIdle", command_id)
        if self._obs_state != ObsState.IDLE:
            self._obs_state = ObsState.IDLE
            self.push_change_event("obsState", self._obs_state)
        self.logger.info("GoToIdle command completed.")
        return [ResultCode.QUEUED], [command_id]

    def is_ObsReset_allowed(self) -> bool:
        """
        Check if command `ObsReset` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: bool
        :raises CommandNotAllowed: command is not allowed
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED_BEFORE_QUEUING
            ):
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("ObsReset Command is allowed")
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ObsReset(self) -> Tuple[List[ResultCode], List[str]]:
        """
        ObsReset Command
        :return: ResultCode and message
        """
        command_id = f"{time.time()}_ObsReset"
        self.logger.info("Instructed simulator to invoke ObsReset command")
        self.update_command_info(OBS_RESET, "")
        if self.defective_params["enabled"]:
            return self.induce_fault("ObsReset", command_id)
        if self._obs_state != ObsState.IDLE:
            self._obs_state = ObsState.IDLE
            self.push_change_event("obsState", self._obs_state)
        self.logger.info("ObsReset command completed.")
        return [ResultCode.QUEUED], [command_id]

    def is_Abort_allowed(self) -> bool:
        """
        Check if command `Abort` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: bool
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
        This method invokes Abort command on subarray devices.
        :return: ResultCode, message
        :rtype: tuple
        """
        command_id = f"{time.time()}_Abort"
        self.logger.info("Instructed simulator to invoke Abort command")
        self.update_command_info(ABORT, "")

        if self._obs_state != ObsState.ABORTED:
            self._obs_state = ObsState.ABORTING
            self.push_change_event("obsState", self._obs_state)
            thread = threading.Timer(
                interval=self._delay,
                function=self.update_device_obsstate,
                args=[ObsState.ABORTED, ABORT],
            )
            thread.start()
            thread = threading.Timer(
                self._delay,
                self.push_command_result,
                args=[ResultCode.OK, ABORT],
                kwargs={"command_id": command_id},
            )
            thread.start()
        self.logger.info("Abort command completed.")
        return [ResultCode.QUEUED], [command_id]

    def is_Restart_allowed(self) -> bool:
        """
        Check if command `Restart` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: bool
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
        This method invokes Restart command on subarray devices
        :return: ResultCode, message
        :rtype: tuple
        """
        command_id = f"{time.time()}_Restart"

        self.logger.info("Instructed simulator to invoke Restart command")
        self.update_command_info(RESTART, "")

        if self._obs_state != ObsState.EMPTY:
            self._obs_state = ObsState.RESTARTING
            self.push_change_event("obsState", self._obs_state)
            thread = threading.Timer(
                interval=self._delay,
                function=self.update_device_obsstate,
                args=[ObsState.EMPTY, RESTART],
            )
            thread.start()
            thread = threading.Timer(
                self._delay,
                self.push_command_result,
                args=[ResultCode.OK, RESTART],
                kwargs={"command_id": command_id},
            )
            thread.start()
        self.logger.info("Restart command completed.")
        return [ResultCode.QUEUED], [command_id]


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
