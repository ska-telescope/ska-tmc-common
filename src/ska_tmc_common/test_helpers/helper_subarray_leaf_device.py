"""
This module implements the Helper devices for subarray leaf nodes for testing
an integrated TMC
"""
# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument
import threading
import time
from typing import List, Tuple

from ska_tango_base.commands import ResultCode
from tango import EnsureOmniThread
from tango.server import command, run

from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice


class HelperSubarrayLeafDevice(HelperBaseDevice):
    """A device exposing commands and attributes of the Subarray Leaf Nodes devices."""

    def is_AssignResources_allowed(self) -> bool:
        """
        This method checks if the AssignResources command is allowed or not
        """
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
        if not self._defective:
            self.logger.info("AssignResource completed.")
            return [ResultCode.OK], [""]
        self.thread = threading.Thread(target=self.start_process)
        self.thread.start()
        self.logger.info("Starting Assign on device %s", self.dev_name)
        return [ResultCode.QUEUED], [""]

    def stop_thread(self):
        """Stops the thread."""
        if self.thread.is_alive():
            self.thread.join()

    def start_process(self):
        """Waits for 5 secs before pushing a longRunningCommandResult event."""
        with EnsureOmniThread():
            time.sleep(5)
            command_id = "1000"
            command_result = (
                command_id,
                f"Exception occured on device: {self.dev_name}",
            )
            self.push_change_event("longRunningCommandResult", command_result)

    def is_Configure_allowed(self) -> bool:
        """
        This method checks the Configure is allowed in the current device
        state.
        :rtype:bool
        """
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
        if not self._defective:
            self.logger.info("Configure completed.")
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]

    def is_Scan_allowed(self) -> bool:
        """
        This method checks if the Scan command is allowed in the current
        device state.
        :rtype:bool
        """
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
        if not self._defective:
            self.logger.info("Scan completed.")
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]

    def is_EndScan_allowed(self) -> bool:
        """
        This method checks if the EndScan command is allowed in the current
        device state.
        :rtype:bool
        """
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
        if not self._defective:
            self.logger.info("EndScan completed.")
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]

    def is_End_allowed(self) -> bool:
        """
        This method checks if the End command is allowed in the current
        device state.
        :rtype:bool
        """
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
        if not self._defective:
            self.logger.info("End completed.")
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]

    def is_GoToIdle_allowed(self) -> bool:
        """
        This method checks if the GoToIdle command is allowed in the current
        device state.
        :rtype:bool
        """
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
        if not self._defective:
            self.logger.info("GoToIdle completed.")
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]

    def is_Abort_allowed(self) -> bool:
        """
        This method checks if the Abort command is allowed in the current
        device state.
        :rtype:bool
        """
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
        self.logger.info("Abort completed.")
        return [ResultCode.OK], [""]

    def is_ObsReset_allowed(self) -> bool:
        """
        This method checks if the ObsReset command is allowed in the current
        device state.
        :rtype:bool
        """
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ObsReset(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This is the method to invoke ObsReset command.
        :return: ResultCode, message
        :rtype: tuple
        """
        if not self._defective:
            self.logger.info("ObsReset completed.")
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]

    def is_Restart_allowed(self) -> bool:
        """
        This method checks if the Restart command is allowed in the current
        device state.
        :rtype:bool
        """
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
        self.logger.info("Restart completed.")
        return [ResultCode.OK], [""]

    def is_ReleaseAllResources_allowed(self) -> bool:
        """
        This method checks if the ReleaseAllResources command is allowed in
        the current device state.
        :return: ResultCode, message
        :rtype: tuple
        """
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
        if not self._defective:
            self.logger.info("ReleaseAllResources completed")
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]

    def is_ReleaseResources_allowed(self) -> bool:
        """
        This method checks if the ReleaseResources command is allowed in the
        current device state.
        :return: ResultCode, message
        :rtype: tuple
        """
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
        if not self._defective:
            self.logger.info("ReleaseResources completed.")
            return [ResultCode.OK], [""]

        return [ResultCode.FAILED], [
            "Device is defective, cannot process command."
        ]

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
