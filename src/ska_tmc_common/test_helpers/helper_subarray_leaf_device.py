"""
This module implements the Helper devices for subarray leaf nodes for testing
an integrated TMC
"""
import json

# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument
import threading
import time
from enum import IntEnum
from typing import List, Optional, Tuple

import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from tango.server import AttrWriteType, attribute, command, run

from ska_tmc_common import CommandNotAllowed, FaultType
from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice


class HelperSubarrayLeafDevice(HelperBaseDevice):
    """A device exposing commands and attributes of the Subarray Leaf Nodes devices."""

    def init_device(self) -> None:
        super().init_device()
        self._delay = 2
        self._obs_state = ObsState.EMPTY
        self._defective = json.dumps(
            {
                "value": False,
                "fault_type": FaultType.NONE,
                "error_message": "",
                "result": ResultCode.FAILED,
            }
        )
        self.defective_params = json.loads(self._defective)

    defective = attribute(dtype=str, access=AttrWriteType.READ)

    delay = attribute(dtype=int, access=AttrWriteType.READ)

    def read_defective(self) -> str:
        """
        Returns defective status of devices

        :rtype: dict
        """
        return self._defective

    def read_delay(self) -> int:
        """This method is used to read the attribute value for delay."""
        return self._delay

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
        for key, value in input_dict.items():
            self.defective_params[key] = value

    @command(
        dtype_in=int,
        doc_in="Set Delay",
    )
    def SetDelay(self, value: int) -> None:
        """Update delay value"""
        self.logger.info("Setting the Delay value to : %s", value)
        self._delay = value

    def inducing_fault(
        self,
        command_name: str,
        fault_type: IntEnum,
        fault_message: str,
        result: ResultCode,
        intermediate_state: Optional[ObsState] = ObsState.RESOURCING,
    ) -> Tuple[List[ResultCode], List[str]]:
        """Induces fault into device according to given parameters"""
        if fault_type == FaultType.FAILED_RESULT:
            return [result], [fault_message]

        if fault_type == FaultType.LONG_RUNNING_EXCEPTION:
            thread = threading.Timer(
                5,
                function=self.push_command_result,
                args=[result, command_name, fault_message],
            )
            thread.start()
            return [ResultCode.QUEUED], [""]

        if fault_type == FaultType.STUCK_IN_INTERMEDIATE_STATE:
            self._obs_state = intermediate_state
            self.push_obs_state_event(intermediate_state)
            return [ResultCode.QUEUED], [""]

        return [ResultCode.OK], [""]

    def push_command_result(
        self, result: ResultCode, command: str, exception: str = ""
    ):
        """Push long running command result event for given command."""
        command_id = f"{time.time()}-{command}"
        if exception:
            command_result = (command_id, exception)
            self.push_change_event("longRunningCommandResult", command_result)
        command_result = (command_id, str(result))
        self.push_change_event("longRunningCommandResult", command_result)

    def push_obs_state_event(self, obs_state: ObsState) -> None:
        """Place holder method. This method will be implemented in the child
        classes."""

    def update_device_obsstate(self, obs_state: ObsState):
        """Updates the device obsState"""
        with tango.EnsureOmniThread():
            self._obs_state = obs_state
            time.sleep(0.1)
            self.push_obs_state_event(self._obs_state)

    def is_AssignResources_allowed(self) -> bool:
        """
        This method checks if the AssignResources command is allowed or not
        """
        if self.defective_params["value"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                raise CommandNotAllowed(
                    "This command is not allowed as device is defective."
                )
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
        if self.defective_params["value"]:
            return self.inducing_fault(
                "AssignResources",
                self.defective_params["fault_type"],
                self.defective_params["error_message"],
                self.defective_params["result"],
                self.defective_params.get("intermidiate_state"),
            )

        self._obs_state = ObsState.RESOURCING
        self.push_obs_state_event(self._obs_state)
        thread = threading.Timer(
            self._delay, self.update_device_obsstate, args=[ObsState.IDLE]
        )
        thread.start()
        self.push_command_result(ResultCode.OK, "AssignResources")
        return [ResultCode.OK], [""]

    def is_Configure_allowed(self) -> bool:
        """
        This method checks the Configure is allowed in the current device
        state.
        :rtype:bool
        """
        if self.defective_params["value"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                raise CommandNotAllowed(
                    "This command is not allowed as device is defective."
                )
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
        if self.defective_params["value"]:
            return self.inducing_fault(
                "Configure",
                self.defective_params["fault_type"],
                self.defective_params["error_message"],
                self.defective_params["result"],
                self.defective_params.get("intermidiate_state"),
            )

        self._obs_state = ObsState.CONFIGURING
        self.push_obs_state_event(self._obs_state)
        thread = threading.Timer(
            self._delay, self.update_device_obsstate, args=[ObsState.READY]
        )
        thread.start()
        self.push_command_result(ResultCode.OK, "Configure")
        return [ResultCode.OK], [""]

    def is_Scan_allowed(self) -> bool:
        """
        This method checks if the Scan command is allowed in the current
        device state.
        :rtype:bool
        """
        if self.defective_params["value"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                raise CommandNotAllowed(
                    "This command is not allowed as device is defective."
                )
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
        if self.defective_params["value"]:
            return self.inducing_fault(
                "Scan",
                self.defective_params["fault_type"],
                self.defective_params["error_message"],
                self.defective_params["result"],
                self.defective_params.get("intermidiate_state"),
            )

        self._obs_state = ObsState.SCANNING
        self.push_obs_state_event(self._obs_state)
        self.push_command_result(ResultCode.OK, "Scan")
        return [ResultCode.OK], [""]

    def is_EndScan_allowed(self) -> bool:
        """
        This method checks if the EndScan command is allowed in the current
        device state.
        :rtype:bool
        """
        if self.defective_params["value"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                raise CommandNotAllowed(
                    "This command is not allowed as device is defective."
                )
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
        if self.defective_params["value"]:
            return self.inducing_fault(
                "EndScan",
                self.defective_params["fault_type"],
                self.defective_params["error_message"],
                self.defective_params["result"],
                self.defective_params.get("intermidiate_state"),
            )

        self._obs_state = ObsState.READY
        self.push_obs_state_event(self._obs_state)
        self.push_command_result(ResultCode.OK, "EndScan")
        return [ResultCode.OK], [""]

    def is_End_allowed(self) -> bool:
        """
        This method checks if the End command is allowed in the current
        device state.
        :rtype:bool
        """
        if self.defective_params["value"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                raise CommandNotAllowed(
                    "This command is not allowed as device is defective."
                )
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
        if self.defective_params["value"]:
            return self.inducing_fault(
                "End",
                self.defective_params["fault_type"],
                self.defective_params["error_message"],
                self.defective_params["result"],
                self.defective_params.get("intermidiate_state"),
            )

        self._obs_state = ObsState.CONFIGURING
        self.push_obs_state_event(self._obs_state)
        thread = threading.Timer(
            self._delay, self.update_device_obsstate, args=[ObsState.IDLE]
        )
        thread.start()
        self.push_command_result(ResultCode.OK, "End")
        return [ResultCode.OK], [""]

    def is_GoToIdle_allowed(self) -> bool:
        """
        This method checks if the GoToIdle command is allowed in the current
        device state.
        :rtype:bool
        """
        if self.defective_params["value"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                raise CommandNotAllowed(
                    "This command is not allowed as device is defective."
                )
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
        if self.defective_params["value"]:
            return self.inducing_fault(
                "GoToIdle",
                self.defective_params["fault_type"],
                self.defective_params["error_message"],
                self.defective_params["result"],
                self.defective_params.get("intermidiate_state"),
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
        if self.defective_params["value"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                raise CommandNotAllowed(
                    "This command is not allowed as device is defective."
                )
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
        if self.defective_params["value"]:
            return self.inducing_fault(
                "Abort",
                self.defective_params["fault_type"],
                self.defective_params["error_message"],
                self.defective_params["result"],
                self.defective_params.get("intermidiate_state"),
            )

        self._obs_state = ObsState.ABORTING
        self.push_obs_state_event(self._obs_state)
        thread = threading.Timer(
            self._delay, self.update_device_obsstate, args=[ObsState.ABORTED]
        )
        thread.start()
        self.push_command_result(ResultCode.OK, "Abort")
        return [ResultCode.OK], [""]

    def is_Restart_allowed(self) -> bool:
        """
        This method checks if the Restart command is allowed in the current
        device state.
        :rtype:bool
        """
        if self.defective_params["value"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                raise CommandNotAllowed(
                    "This command is not allowed as device is defective."
                )
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
        if self.defective_params["value"]:
            return self.inducing_fault(
                "Restart",
                self.defective_params["fault_type"],
                self.defective_params["error_message"],
                self.defective_params["result"],
                self.defective_params.get("intermidiate_state"),
            )

        self._obs_state = ObsState.RESTARTING
        self.push_obs_state_event(self._obs_state)
        thread = threading.Timer(
            self._delay, self.update_device_obsstate, args=[ObsState.EMPTY]
        )
        thread.start()
        self.push_command_result(ResultCode.OK, "Restart")
        return [ResultCode.OK], [""]

    def is_ReleaseAllResources_allowed(self) -> bool:
        """
        This method checks if the ReleaseAllResources command is allowed in
        the current device state.
        :return: ResultCode, message
        :rtype: tuple
        """
        if self.defective_params["value"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                raise CommandNotAllowed(
                    "This command is not allowed as device is defective."
                )
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
        if self.defective_params["value"]:
            return self.inducing_fault(
                "ReleaseAllResources",
                self.defective_params["fault_type"],
                self.defective_params["error_message"],
                self.defective_params["result"],
                self.defective_params.get("intermidiate_state"),
            )

        self._obs_state = ObsState.RESOURCING
        self.push_obs_state_event(self._obs_state)
        thread = threading.Timer(
            self._delay, self.update_device_obsstate, args=[ObsState.EMPTY]
        )
        thread.start()
        self.push_command_result(ResultCode.OK, "ReleaseAllResources")
        return [ResultCode.OK], [""]

    def is_ReleaseResources_allowed(self) -> bool:
        """
        This method checks if the ReleaseResources command is allowed in the
        current device state.
        :return: ResultCode, message
        :rtype: tuple
        """
        if self.defective_params["value"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                raise CommandNotAllowed(
                    "This command is not allowed as device is defective."
                )
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
        if self.defective_params["value"]:
            return self.inducing_fault(
                "ReleaseResources",
                self.defective_params["fault_type"],
                self.defective_params["error_message"],
                self.defective_params["result"],
                self.defective_params.get("intermidiate_state"),
            )

        self._obs_state = ObsState.RESOURCING
        self.push_obs_state_event(self._obs_state)
        thread = threading.Timer(
            self._delay, self.update_device_obsstate, args=[ObsState.IDLE]
        )
        thread.start()
        self.push_command_result(ResultCode.OK, "ReleaseResources")
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
