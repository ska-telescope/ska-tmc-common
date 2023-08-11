"""
This module implements the Helper MCCS subarray devices for testing
an integrated TMC
"""
# pylint: disable=unused-argument
import json
import threading
from typing import List, Tuple

from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from tango import AttrWriteType
from tango.server import attribute, command

from ska_tmc_common import FaultType
from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice


# pylint: disable=attribute-defined-outside-init
class HelperMCCSStateDevice(HelperBaseDevice):
    """A generic device for triggering state changes with a command"""

    def init_device(self) -> None:
        super().init_device()
        self.dev_name = self.get_name()
        self._isSubsystemAvailable = False
        self._raise_exception = False
        self._defective = json.dumps(
            {
                "enabled": False,
                "fault_type": FaultType.FAILED_RESULT,
                "error_message": "Default exception.",
                "result": ResultCode.FAILED,
            }
        )
        self.defective_params = json.loads(self._defective)

    class InitCommand(SKABaseDevice.InitCommand):
        """A class for the HelperMccsStateDevice's init_device() "command"."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            :returns: ResultCode, message
            :rtype:tuple
            """
            super().do()
            self._device._assigned_resources = "{ }"
            self._device.set_change_event("assignedResources", True, False)
            return (ResultCode.OK, "")

    assignedResources = attribute(dtype="DevString", access=AttrWriteType.READ)

    def read_assignedResources(self) -> str:
        """
        Reads the values of the assignedResources
        :rtype:str
        """
        return self._device._assigned_resources

    def is_AssignResources_allowed(self) -> bool:
        """
        Check if command `AssignResources` is allowed in the current device
        state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command(
        dtype_in="DevString",
        doc_in="JSON-encoded string with the resources to add to subarray",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def AssignResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes AssignResources command on subarray device

        :return: a tuple containing ResultCode and Message
        :rtype: Tuple
        """
        # pylint:disable=line-too-long
        assigned_resources = {
            "interface": "https://schema.skatelescope.org/ska-low-mccs-assignedresources/1.0",
            "subarray_beam_ids": [1],
            "station_ids": [[1, 2]],
            "channel_blocks": [3],
        }
        # pylint:enable=line-too-long
        self._assigned_resources = json.dumps(assigned_resources)
        self.push_change_event("assignedResources", self._assigned_resources)
        return [ResultCode.OK], [""]

    def induce_fault(
        self,
        command_name: str,
    ) -> Tuple[List[ResultCode], List[str]]:
        """Induces fault into device according to given parameters

        :params:

        command_name: Name of the command for which fault is being induced
        dtype: str
        rtype: Tuple[List[ResultCode], List[str]]
        """
        fault_type = self.defective_params["fault_type"]
        result = self.defective_params["result"]
        fault_message = self.defective_params["error_message"]
        intermediate_state = (
            self.defective_params.get("intermediate_state")
            or ObsState.RESOURCING
        )

        if fault_type == FaultType.FAILED_RESULT:
            return [result], [fault_message]

        if fault_type == FaultType.LONG_RUNNING_EXCEPTION:
            thread = threading.Timer(
                self._delay,
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
        for key, value in input_dict.items():
            self.defective_params[key] = value

    def is_ReleaseResources_allowed(self) -> bool:
        """
        Check if command `ReleaseResources` is allowed in the current
        device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command(
        dtype_in="DevString",
        doc_in="JSON-encoded string with the resources to remove from the \
            subarray",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ReleaseResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes ReleaseResources command on subarray device

        :return: a tuple conataining Resultcose and Message
        :rtype: Tuple
        """
        # pylint:disable=line-too-long
        tmpDict = {
            "interface": "https://schema.skatelescope.org/ska-low-mccs-assignedresources/1.0",
            "subarray_beam_ids": [],
            "station_ids": [],
            "channel_blocks": [],
        }
        # pylint:enable=line-too-long
        self._assigned_resources = json.dumps(tmpDict)
        return [ResultCode.OK], [""]
