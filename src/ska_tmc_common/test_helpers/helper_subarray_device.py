"""
This module implements the Helper devices for subarray nodes for testing
an integrated TMC
"""
# pylint: disable=attribute-defined-outside-init
import json
import threading
import time
from enum import IntEnum
from logging import Logger
from typing import Any, Callable, List, Optional, Tuple

import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import HealthState, ObsState
from ska_tango_base.subarray import SKASubarray, SubarrayComponentManager
from tango import AttrWriteType, DevState, EnsureOmniThread
from tango.server import attribute, command, run


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


class HelperSubArrayDevice(SKASubarray):
    """A generic subarray device for triggering state changes with a command.
    It can be used as helper device for element subarray node"""

    def init_device(self):
        super().init_device()
        self._health_state = HealthState.OK
        self._command_in_progress = ""
        self._defective = False
        self._delay = 2
        self._raise_exception = False

    class InitCommand(SKASubarray.InitCommand):
        """A class for the HelperSubarrayDevice's init_device() "command"."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            """
            super().do()
            self._device._receive_addresses = (
                '{"science_A":{"host":[[0,"192.168.0.1"],[2000,"192.168.0.1"]],"port":['
                '[0,9000,1],[2000,9000,1]]},"target:a":{"vis0":{'
                '"function":"visibilities","host":[[0,'
                '"proc-pb-test-20220916-00000-test-receive-0.receive.test-sdp"]],'
                '"port":[[0,9000,1]]}},"calibration:b":{"vis0":{'
                '"function":"visibilities","host":[[0,'
                '"proc-pb-test-20220916-00000-test-receive-0.receive.test-sdp"]],'
                '"port":[[0,9000,1]]}}}'
            )
            self._device.set_change_event("State", True, False)
            self._device.set_change_event("obsState", True, False)
            self._device.set_change_event("commandInProgress", True, False)
            self._device.set_change_event("healthState", True, False)
            self._device.set_change_event("receiveAddresses", True, False)
            self._device.set_change_event(
                "longRunningCommandResult", True, False
            )
            return ResultCode.OK, ""

    commandInProgress = attribute(dtype="DevString", access=AttrWriteType.READ)

    receiveAddresses = attribute(dtype="DevString", access=AttrWriteType.READ)

    defective = attribute(dtype=bool, access=AttrWriteType.READ)

    delay = attribute(dtype=int, access=AttrWriteType.READ)

    raiseException = attribute(dtype=bool, access=AttrWriteType.READ)

    def read_delay(self) -> int:
        """This method is used to read the attribute value for delay."""
        return self._delay

    def read_raiseException(self) -> bool:
        """This method is used to read the attribute value for raise exception

        :rtype: bool
        """
        return self._raise_exception

    def read_receiveAddresses(self) -> str:
        """
        This method is used to read receiveAddresses attribute
        :rtype:str
        """
        return self._receive_addresses

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

    def update_device_obsstate(self, value: IntEnum) -> None:
        """Updates the given data after a delay."""
        with tango.EnsureOmniThread():
            time.sleep(self._delay)
            self._obs_state = value
            time.sleep(0.1)
            self.push_change_event("obsState", self._obs_state)

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
    def SetDefective(self, value: bool) -> None:
        """
        Trigger defective change
        :rtype: bool
        """
        self.logger.info("Setting the defective value to : %s", value)
        self._defective = value

    @command(
        dtype_in=bool,
        doc_in="Raise Exception",
    )
    def SetRaiseException(self, value: bool) -> None:
        """Set Raise Exception"""
        self.logger.info("Setting the raise exception value to : %s", value)
        self._raise_exception = value

    @command(
        dtype_in=int,
        doc_in="Set Delay",
    )
    def SetDelay(self, value: int) -> None:
        """Update delay value"""
        self.logger.info("Setting the Delay value to : %s", value)
        self._delay = value

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
        value = HealthState(argin)
        if self._health_state != value:
            self._health_state = HealthState(argin)
            self.push_change_event("healthState", self._health_state)

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
        if not self._defective:
            if self.dev_state() != DevState.ON:
                self.set_state(DevState.ON)
                self.push_change_event("State", self.dev_state())
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is Defective, cannot process command."
        ]

    def is_Off_allowed(self) -> bool:
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Off(self) -> Tuple[List[ResultCode], List[str]]:
        if not self._defective:
            if self.dev_state() != DevState.OFF:
                self.set_state(DevState.OFF)
                self.push_change_event("State", self.dev_state())
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is Defective, cannot process command."
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
        if not self._defective:
            if self.dev_state() != DevState.STANDBY:
                self.set_state(DevState.STANDBY)
                self.push_change_event("State", self.dev_state())
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is Defective, cannot process command."
        ]

    def is_AssignResources_allowed(self) -> bool:
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
    def AssignResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes AssignResources command on subarray devices
        """
        if self._defective:
            self._obs_state = ObsState.RESOURCING
            self.push_change_event("obsState", self._obs_state)
            return [ResultCode.FAILED], [
                "Device is Defective, cannot process command completely."
            ]

        input = json.loads(argin)
        if "eb_id" not in input["execution_block"]:
            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "eb_id not found in the input json string",
                "SdpSubarry.AssignResources",
                tango.ErrSeverity.ERR,
            )

        elif self._obs_state != ObsState.IDLE:
            self._obs_state = ObsState.RESOURCING
            self.push_change_event("obsState", self._obs_state)
            thread = threading.Thread(
                target=self.update_device_obsstate, args=[ObsState.IDLE]
            )
            thread.start()
        return [ResultCode.OK], [
            "AssignResources invoked successfully on SdpSubarray."
        ]

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
        Check if command `ReleaseResources` is allowed in the current device state.

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
        if not self._defective:
            if self._obs_state != ObsState.EMPTY:
                self._obs_state = ObsState.EMPTY
                self.push_change_event("obsState", self._obs_state)
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is Defective, cannot process command."
        ]

    def is_ReleaseAllResources_allowed(self) -> bool:
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
    def ReleaseAllResources(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes ReleaseAllResources command on
        subarray device
        :return: ResultCode, message
        :rtype: tuple
        """
        if not self._defective:
            if self._obs_state != ObsState.EMPTY:
                self._obs_state = ObsState.EMPTY
                self.push_change_event("obsState", self._obs_state)
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is Defective, cannot process command."
        ]

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
        if not self._defective:
            if self._obs_state in [ObsState.READY, ObsState.IDLE]:
                self._obs_state = ObsState.CONFIGURING
                self.push_change_event("obsState", self._obs_state)
                thread = threading.Thread(
                    target=self.update_device_obsstate, args=[ObsState.READY]
                )
                thread.start()
            return [ResultCode.OK], [""]
        self._obs_state = ObsState.CONFIGURING
        self.push_change_event("obsState", self._obs_state)
        return [ResultCode.FAILED], [
            "Device is Defective, cannot process command completely."
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
        if not self._defective:
            if self._obs_state != ObsState.SCANNING:
                self._obs_state = ObsState.SCANNING
                self.push_change_event("obsState", self._obs_state)
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is Defective, cannot process command."
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
        if not self._defective:
            if self._obs_state != ObsState.READY:
                self._obs_state = ObsState.READY
                self.push_change_event("obsState", self._obs_state)
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is Defective, cannot process command."
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
        if not self._defective:
            if self._obs_state != ObsState.IDLE:
                self._obs_state = ObsState.IDLE
                self.push_change_event("obsState", self._obs_state)
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is Defective, cannot process command."
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
        if not self._defective:
            if self._obs_state != ObsState.IDLE:
                self._obs_state = ObsState.IDLE
                self.push_change_event("obsState", self._obs_state)
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is Defective, cannot process command."
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
        if not self._defective:
            if self._obs_state != ObsState.IDLE:
                self._obs_state = ObsState.IDLE
                self.push_change_event("obsState", self._obs_state)
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is Defective, cannot process command."
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
        if self._obs_state != ObsState.ABORTED:
            self._obs_state = ObsState.ABORTING
            self.push_change_event("obsState", self._obs_state)
            thread = threading.Thread(
                target=self.update_device_obsstate, args=[ObsState.ABORTED]
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
        if self._obs_state != ObsState.EMPTY:
            self._obs_state = ObsState.RESTARTING
            self.push_change_event("obsState", self._obs_state)
            thread = threading.Thread(
                target=self.update_device_obsstate, args=[ObsState.EMPTY]
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
