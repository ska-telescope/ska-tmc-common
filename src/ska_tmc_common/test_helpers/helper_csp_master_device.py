"""
This module defines a helper device that acts as csp master in our testing.
"""

# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument
import time
from typing import List, Tuple

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from tango import DevState
from tango.server import command, run

from ska_tmc_common import CommandNotAllowed, FaultType
from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice


class HelperCspMasterDevice(HelperBaseDevice):
    """A helper device class for Csp Controller device"""

    def init_device(self):
        super().init_device()
        self._delay = 2
        self._obs_state = ObsState.EMPTY

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
        dtype_in="DevVarStringArray",
        doc_in="Input argument as an empty list",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def On(self, argin: list) -> Tuple[List[ResultCode], List[str]]:
        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault(
                "On",
            )
        if self.dev_state() != DevState.ON:
            self.set_state(DevState.ON)
            time.sleep(0.1)
            self.push_change_event("State", self.dev_state())
            self.logger.info("On command completed.")
            return [ResultCode.OK], [""]
        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]

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
        dtype_in="DevVarStringArray",
        doc_in="Input argument as an empty list",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Off(self, argin: list) -> Tuple[List[ResultCode], List[str]]:
        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault(
                "On",
            )
        if self.dev_state() != DevState.OFF:
            self.set_state(DevState.OFF)
            time.sleep(0.1)
            self.push_change_event("State", self.dev_state())
            self.logger.info("Off command completed.")
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]

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
        self.logger.info("On Command is allowed")
        return True

    @command(
        dtype_in="DevVarStringArray",
        doc_in="Input argument as an empty list",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Standby(self, argin: list) -> Tuple[List[ResultCode], List[str]]:
        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault(
                "On",
            )
        if self.dev_state() != DevState.STANDBY:
            self.set_state(DevState.STANDBY)
            time.sleep(0.1)
            self.push_change_event("State", self.dev_state())
            self.logger.info("Standby command completed.")
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
