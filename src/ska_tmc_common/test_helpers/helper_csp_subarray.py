"""
This module implements the Helper devices for subarray nodes for testing
an integrated TMC
"""
# pylint: disable=attribute-defined-outside-init
import threading
import time
from typing import List, Tuple

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from tango import EnsureOmniThread
from tango.server import command, run

from ska_tmc_common import HelperSubArrayDevice


class HelperCspSubarray(HelperSubArrayDevice):
    """A  helper CspSubarray device to mock CSP Subarray behaviour
    of returing the command result."""

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
        self.logger.info("CSP Helper Subarray AssignResources command")
        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault(
                "AssignResources",
            )

        if self._raise_exception:
            self._obs_state = ObsState.RESOURCING
            self.push_change_event("obsState", self._obs_state)
            self.thread = threading.Thread(
                target=self.wait_and_update_exception, args=["AssignResources"]
            )
            self.thread.start()
            return [ResultCode.QUEUED], [""]

        self._obs_state = ObsState.RESOURCING
        self.push_change_event("obsState", self._obs_state)

        command_result_thread = threading.Thread(
            target=self.wait_and_update_command_result,
            args=["AssignResources"],
        )
        command_result_thread.start()

        thread = threading.Thread(
            target=self.update_device_obsstate, args=[ObsState.IDLE]
        )
        thread.start()
        self.logger.debug(
            "AssignResourse invoked obsstate is transition \
                          to Resourcing"
        )
        return [ResultCode.OK], [""]

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

    def wait_and_update_command_result(self, command_name):
        """Waits for 5 secs before pushing a longRunningCommandResult event."""
        with EnsureOmniThread():
            time.sleep(5)
            command_id = f"1000_{command_name}"
            command_result = (
                command_id,
                str([ResultCode.OK, f"command {command_name} completed"]),
            )
            self.push_change_event("longRunningCommandResult", command_result)

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ReleaseResources(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes ReleaseResources command on subarray device
        """
        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault(
                "ReleaseResources",
            )
        if self._obs_state != ObsState.EMPTY:
            self._obs_state = ObsState.EMPTY
            self.push_change_event("obsState", self._obs_state)
        return [ResultCode.OK], [""]

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
        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault(
                "ReleaseAllResources",
            )

        if self._raise_exception:
            self._obs_state = ObsState.RESOURCING
            self.push_change_event("obsState", self._obs_state)
            self.thread = threading.Thread(
                target=self.wait_and_update_exception,
                args=["ReleaseAllResources"],
            )
            self.thread.start()
            return [ResultCode.QUEUED], [""]

        self._obs_state = ObsState.RESOURCING
        self.push_change_event("obsState", self._obs_state)

        command_result_thread = threading.Thread(
            target=self.wait_and_update_command_result,
            args=["ReleaseAllResources"],
        )
        command_result_thread.start()

        thread = threading.Thread(
            target=self.update_device_obsstate, args=[ObsState.EMPTY]
        )
        thread.start()
        self.logger.debug(
            "ReleaseAllResources invoked obsstate is transition \
                          to Resourcing"
        )
        return [ResultCode.OK], [""]

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
        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault(
                "Configure",
            )
        if self._obs_state in [ObsState.READY, ObsState.IDLE]:
            self._obs_state = ObsState.CONFIGURING
            self.push_change_event("obsState", self._obs_state)

            command_result_thread = threading.Thread(
                target=self.wait_and_update_command_result,
                args=["Configure"],
            )
            command_result_thread.start()

            thread = threading.Thread(
                target=self.update_device_obsstate, args=[ObsState.READY]
            )
            thread.start()
        self.logger.info("Configure command completed.")
        return [ResultCode.OK], [""]

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
        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault(
                "Scan",
            )
        if self._obs_state != ObsState.SCANNING:
            self._obs_state = ObsState.SCANNING

            command_result_thread = threading.Thread(
                target=self.wait_and_update_command_result, args=["Scan"]
            )
            command_result_thread.start()

            self.push_change_event("obsState", self._obs_state)
        self.logger.debug(
            "Scan invoked obsstate is transition \
                          to SCANNING"
        )
        return [ResultCode.OK], [""]

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
        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault(
                "EndScan",
            )
        if self._obs_state != ObsState.READY:
            self._obs_state = ObsState.READY

            command_result_thread = threading.Thread(
                target=self.wait_and_update_command_result,
                args=["EndScan"],
            )
            command_result_thread.start()

            self.push_change_event("obsState", self._obs_state)
        self.logger.info("EndScan command completed.")
        return [ResultCode.OK], [""]

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
        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault(
                "GoToIdle",
            )
        if self._obs_state != ObsState.IDLE:
            self._obs_state = ObsState.IDLE
            command_result_thread = threading.Thread(
                target=self.wait_and_update_command_result,
                args=["GoToIdle"],
            )
            command_result_thread.start()

            self.push_change_event("obsState", self._obs_state)
        self.logger.info("GoToIdle command completed.")
        return [ResultCode.OK], [""]

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ObsReset(self) -> Tuple[List[ResultCode], List[str]]:
        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault(
                "ObsReset",
            )
        if self._obs_state != ObsState.IDLE:
            self._obs_state = ObsState.IDLE

            command_result_thread = threading.Thread(
                target=self.wait_and_update_command_result,
                args=["ObsReset"],
            )
            command_result_thread.start()

            self.push_change_event("obsState", self._obs_state)
        self.logger.info("ObsReset command completed.")
        return [ResultCode.OK], [""]

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
        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault(
                "Abort",
            )
        if self._obs_state != ObsState.ABORTED:
            self._obs_state = ObsState.ABORTING
            self.push_change_event("obsState", self._obs_state)

            command_result_thread = threading.Thread(
                target=self.wait_and_update_command_result, args=["Abort"]
            )
            command_result_thread.start()

            thread = threading.Thread(
                target=self.update_device_obsstate, args=[ObsState.ABORTED]
            )
            thread.start()
        self.logger.info("Abort command completed.")
        return [ResultCode.OK], [""]

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
        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault(
                "Restart",
            )
        if self._obs_state != ObsState.EMPTY:
            self._obs_state = ObsState.RESTARTING
            self.push_change_event("obsState", self._obs_state)

            command_result_thread = threading.Thread(
                target=self.wait_and_update_command_result, args=["Restart"]
            )
            command_result_thread.start()

            thread = threading.Thread(
                target=self.update_device_obsstate, args=[ObsState.EMPTY]
            )
            thread.start()
        self.logger.info("Restart command completed.")
        return [ResultCode.OK], [""]


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """
    Runs the HelperCspSubArray Tango device.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: integer. Exit code of the run method.
    """
    return run((HelperCspSubarray,), args=args, **kwargs)


if __name__ == "__main__":
    main()