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

from ska_tmc_common.test_helpers.empty_component_manager import (
    EmptyComponentManager,
)


# pylint: disable=attribute-defined-outside-init
class HelperBaseDevice(SKABaseDevice):
    """A common base device for helper devices."""

    def init_device(self) -> None:
        super().init_device()
        self._health_state = HealthState.OK
        self._defective = False
        self.dev_name = self.get_name()
        self._isSubsystemAvailable = False

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
        dtype_in=bool,
        doc_in="Set Defective",
    )
    def SetDefective(self, value: bool) -> None:
        """
        Trigger defective change
        :param: value
        :type: bool
        """
        self._defective = value

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
        if not self._defective:
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
        if not self._defective:
            value = HealthState(argin)
            if self._health_state != value:
                self._health_state = HealthState(argin)
                self.push_change_event("healthState", self._health_state)

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
            "Device is Defective, cannot process command."
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
            "Device is Defective, cannot process command."
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
