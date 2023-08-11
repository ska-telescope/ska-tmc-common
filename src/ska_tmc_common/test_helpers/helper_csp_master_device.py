"""
This module defines a helper device that acts as csp master in our testing.
"""
# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument
import time
from typing import List, Tuple

from ska_tango_base.commands import ResultCode
from tango import DevState
from tango.server import command, run

from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice
import json
from ska_tmc_common import  FaultType
from ska_tango_base.control_model import ObsState
import threading
class HelperCspMasterDevice(HelperBaseDevice):
    """A helper device class for Csp Controller device"""
    
    def init_device(self):
        super().init_device()
        self._delay = 2
        self._obs_state = ObsState.EMPTY
        self._defective = json.dumps(
            {
                "enabled": False,
                "fault_type": FaultType.FAILED_RESULT,
                "error_message": "Default exception.",
                "result": ResultCode.FAILED,
            }
        )
        self.defective_params = json.loads(self._defective)
        
    def is_On_allowed(self) -> bool:
        return True
    
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
            
    @command(
        dtype_in="DevVarStringArray",
        doc_in="Input argument as an empty list",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def On(self, argin: list) -> Tuple[List[ResultCode], List[str]]:
        if not self._defective:
            if self.dev_state() != DevState.ON:
                self.set_state(DevState.ON)
                time.sleep(0.1)
                self.push_change_event("State", self.dev_state())
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]

    def is_Off_allowed(self) -> bool:
        return True

    @command(
        dtype_in="DevVarStringArray",
        doc_in="Input argument as an empty list",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Off(self, argin: list) -> Tuple[List[ResultCode], List[str]]:
        if not self._defective:
            if self.dev_state() != DevState.OFF:
                self.set_state(DevState.OFF)
                time.sleep(0.1)
                self.push_change_event("State", self.dev_state())
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]

    def is_Standby_allowed(self) -> bool:
        return True

    @command(
        dtype_in="DevVarStringArray",
        doc_in="Input argument as an empty list",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Standby(self, argin: list) -> Tuple[List[ResultCode], List[str]]:
        if not self._defective:
            if self.dev_state() != DevState.STANDBY:
                self.set_state(DevState.STANDBY)
                time.sleep(0.1)
                self.push_change_event("State", self.dev_state())
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """
    Runs the HelperCspMasterDevice Tango device.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: integer. Exit code of the run method.
    """
    return run((HelperCspMasterDevice,), args=args, **kwargs)


if __name__ == "__main__":
    main()
