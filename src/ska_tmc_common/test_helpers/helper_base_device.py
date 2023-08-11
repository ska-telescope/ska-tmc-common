"""
A common module for different helper devices(mock devices)"
"""
import time
from typing import List, Tuple
import tango
from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import HealthState
from tango import DevState
from tango.server import AttrWriteType, attribute, command, run
from ska_tango_base.control_model import ObsState
from ska_tmc_common.test_helpers.empty_component_manager import (
    EmptyComponentManager,
)
import json
from ska_tmc_common import  FaultType
import threading

# pylint: disable=attribute-defined-outside-init
class HelperBaseDevice(SKABaseDevice):
    """A common base device for helper devices."""

    def init_device(self) -> None:
        super().init_device()
        self._health_state = HealthState.OK
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
        """A class for the HelperBaseDevice's init_device() command."""

        def do(self) -> Tuple[ResultCode, str]:
            super().do()
            self._device.set_change_event("State", True, False)
            self._device.set_change_event("healthState", True, False)
            self._device.set_change_event(
                "longRunningCommandResult", True, False
            )
            self._device.set_change_event("isSubsystemAvailable", True, False)
            return (ResultCode.OK, "")

    def create_component_manager(self) -> EmptyComponentManager:
        """
        Creates an instance of EmptyComponentManager
        :rtype:class
        """
        cm = EmptyComponentManager(
            logger=self.logger,
            max_workers=1,
            communication_state_callback=None,
            component_state_callback=None,
        )
        return cm

    defective = attribute(dtype=bool, access=AttrWriteType.READ)

    isSubsystemAvailable = attribute(dtype=bool, access=AttrWriteType.READ)

    raiseException = attribute(dtype=bool, access=AttrWriteType.READ)

    def read_raiseException(self) -> bool:
        """This method is used to read the attribute value for raise exception

        :rtype: bool
        """
        return self._raise_exception

    def read_defective(self) -> bool:
        """
        Returns defective status of devices

        :rtype: bool
        """
        return self._defective

    def read_isSubsystemAvailable(self) -> bool:
        """
        Returns avalability status for the leaf nodes devices

        :rtype: bool
        """
        return self._isSubsystemAvailable

    def always_executed_hook(self) -> None:
        pass

    def delete_device(self) -> None:
        pass
        
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
        dtype_in="DevState",
        doc_in="state to assign",
    )
    def SetDirectState(self, argin: tango.DevState) -> None:
        """
        Trigger a DevState change

        :param tango.DevState
        """
        # import debugpy; debugpy.debug_this_thread()
        if self.dev_state() != argin:
            self.set_state(argin)
            time.sleep(0.1)
            self.push_change_event("State", self.dev_state())

    @command(
        dtype_in=bool,
        doc_in="Set Availability of the device",
    )
    def SetisSubsystemAvailable(self, value: bool) -> None:
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
        dtype_in=int,
        doc_in="state to assign",
    )
    def SetDirectHealthState(self, argin: HealthState) -> None:
        """
        Trigger a HealthState change
        :param tango.DevState
        """
        # import debugpy; debugpy.debug_this_thread()
        value = HealthState(argin)
        if self._health_state != value:
            self._health_state = HealthState(argin)
            self.push_change_event("healthState", self._health_state)

    @command(
        dtype_in=bool,
        doc_in="Raise Exception",
    )
    def SetRaiseException(self, value: bool) -> None:
        """Set Raise Exception"""
        self.logger.info("Setting the raise exception value to : %s", value)
        self._raise_exception = value

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
                time.sleep(0.1)
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
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Standby(self) -> Tuple[List[ResultCode], List[str]]:
        if not self._defective:
            if self.dev_state() != DevState.STANDBY:
                self.set_state(DevState.STANDBY)
                time.sleep(0.1)
                self.push_change_event("State", self.dev_state())
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]

    def is_disable_allowed(self) -> bool:
        "Checks if disable command is allowed"
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Disable(self) -> Tuple[List[ResultCode], List[str]]:
        """
        It sets the DevState to disable.
        :rtype: Tuple
        """
        if not self._defective:
            if self.dev_state() != DevState.DISABLE:
                self.set_state(DevState.DISABLE)
                time.sleep(0.1)
                self.push_change_event("State", self.dev_state())
            return [ResultCode.OK], ["Disable command invoked on SDP Master"]

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """
    Runs the HelperBaseDevice Tango device.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: integer. Exit code of the run method.
    """
    return run((HelperBaseDevice,), args=args, **kwargs)


if __name__ == "__main__":
    main()
