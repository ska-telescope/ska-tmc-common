# pylint: disable=attribute-defined-outside-init, too-many-ancestors
"""Helper device for SdpSubarray device"""
import json
from typing import List, Tuple

import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from tango import AttrWriteType, DevState
from tango.server import attribute, command, run

from ska_tmc_common import HelperSubArrayDevice


class HelperSdpSubarray(HelperSubArrayDevice):
    """A  helper SdpSubarray device for triggering state changes with a
    command.
    It can be used to mock SdpSubarray's bahavior to test error propagation
    from SdpSubarray to SdpSubarrayLeafNode in case of command failure"""

    def init_device(self):
        super().init_device()
        self._state = DevState.OFF
        # pylint:disable=line-too-long
        self._receive_addresses = (
            '{"science_A":{"host":[[0,"192.168.0.1"],[2000,"192.168.0.1"]],"port":['
            '[0,9000,1],[2000,9000,1]]},"target:a":{"vis0":{'
            '"function":"visibilities","host":[[0,'
            '"proc-pb-test-20220916-00000-test-receive-0.receive.test-sdp"]],'
            '"port":[[0,9000,1]]}},"calibration:b":{"vis0":{'
            '"function":"visibilities","host":[[0,'
            '"proc-pb-test-20220916-00000-test-receive-0.receive.test-sdp"]],'
            '"port":[[0,9000,1]]}}}'
        )
        # pylint:enable=line-too-long

    receiveAddresses = attribute(
        label="Receive addresses",
        dtype=str,
        access=AttrWriteType.READ,
        doc="Host addresses for visibility receive as a JSON string.",
    )

    def read_receiveAddresses(self):
        """Returns receive addresses."""
        return self._receive_addresses

    def is_On_allowed(self):
        """
        Check if command `On` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def On(self) -> Tuple[List[ResultCode], List[str]]:
        """This method invokes On command on SdpSubarray device."""
        if self.dev_state() != DevState.ON:
            self.set_state(DevState.ON)
            return ([ResultCode.OK], [""])
        return ([ResultCode.FAILED], ["cannot process command."])

    def is_Off_allowed(self):
        """
        Check if command `Off` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Off(self) -> Tuple[List[ResultCode], List[str]]:
        """This method invokes Off command on SdpSubarray device."""
        if self.dev_state() != DevState.OFF:
            self.set_state(DevState.OFF)
            return ([ResultCode.OK], [""])
        return ([ResultCode.FAILED], ["cannot process command."])

    def is_AssignResources_allowed(self):
        """
        Check if command `AssignResources` is allowed in the current device
        state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format.",
        doc_out="(ReturnType, 'DevVarLongStringArray')",
    )
    def AssignResources(self, argin) -> Tuple[List[ResultCode], List[str]]:
        """This method invokes AssignResources command on SdpSubarray
        device."""
        if self._defective:
            self.raise_exception_for_defective_device(
                command_name="SdpSubarray.AssignResources"
            )

        self.logger.info("Argin on SdpSubarray helper: %s", argin)
        input = json.loads(argin)

        if "eb_id" not in input["execution_block"]:
            self.logger.info("Missing eb_id in the AssignResources input json")
            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "Missing eb_id in the AssignResources input json",
                "SdpSubarry.AssignResources()",
                tango.ErrSeverity.ERR,
            )

        if self._obs_state != ObsState.IDLE:
            self._obs_state = ObsState.IDLE
            self.push_change_event("obsState", self._obs_state)
        return ([ResultCode.OK], [""])

    def is_ReleaseResources_allowed(self):
        """
        Check if command `ReleaseResources` is allowed in the current device
        state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ReleaseResources(self) -> Tuple[List[ResultCode], List[str]]:
        """This method invokes ReleaseResources command on SdpSubarray
        device."""
        if self._defective:
            self.raise_exception_for_defective_device(
                command_name="SdpSubarray.ReleaseResources"
            )

        if not self._defective:
            if self._obs_state != ObsState.EMPTY:
                self._obs_state = ObsState.EMPTY
                self.push_change_event("obsState", self._obs_state)
        return ([ResultCode.OK], [""])

    def is_ReleaseAllResources_allowed(self):
        """
        Check if command `ReleaseAllResources` is allowed in the current
        device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ReleaseAllResources(self) -> Tuple[List[ResultCode], List[str]]:
        """This method invokes ReleaseAllResources command on SdpSubarray
        device."""
        if self._defective:
            self.raise_exception_for_defective_device(
                command_name="SdpSubarray.ReleaseAllResources"
            )

        if not self._defective:
            if self._obs_state != ObsState.EMPTY:
                self._obs_state = ObsState.EMPTY
                self.push_change_event("obsState", self._obs_state)
        return ([ResultCode.OK], [""])

    def is_Configure_allowed(self):
        """
        Check if command `Configure` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format.",
        doc_out="(ReturnType, 'DevVarLongStringArray')",
    )
    def Configure(self, argin) -> Tuple[List[ResultCode], List[str]]:
        """This method invokes Configure command on SdpSubarray device."""
        if self._defective:
            self.raise_exception_for_defective_device(
                command_name="SdpSubarray.Configure"
            )

        input = json.loads(argin)
        if "scan_type" not in input:
            self.logger.info(
                "Missing scan_type in the AssignResources input json"
            )
            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "Missing scan_type in the AssignResources input json",
                "SdpSubarry.Configure()",
                tango.ErrSeverity.ERR,
            )

        if self._obs_state != ObsState.READY:
            self._obs_state = ObsState.READY
            self.push_change_event("obsState", self._obs_state)
        return ([ResultCode.OK], [""])

    def is_Scan_allowed(self):
        """
        Check if command `Scan` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format.",
        doc_out="(ReturnType, 'DevVarLongStringArray')",
    )
    def Scan(self, argin) -> Tuple[List[ResultCode], List[str]]:
        """This method invokes Scan command on SdpSubarray device."""
        if self._defective:
            self.raise_exception_for_defective_device(
                command_name="SdpSubarray.Scan"
            )

        input = json.loads(argin)
        if "scan_id" not in input:
            self.logger.info(
                "Missing scan_id in the AssignResources input json"
            )
            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "Missing scan_id in the AssignResources input json",
                "SdpSubarry.Configure()",
                tango.ErrSeverity.ERR,
            )

        if self._obs_state != ObsState.SCANNING:
            self._obs_state = ObsState.SCANNING
            self.push_change_event("obsState", self._obs_state)
        return ([ResultCode.OK], [""])

    def is_EndScan_allowed(self):
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
        """This method invokes EndScan command on SdpSubarray device."""
        if self._defective:
            self.raise_exception_for_defective_device(
                command_name="SdpSubarray.EndScan"
            )

        if not self._defective:
            if self._obs_state != ObsState.READY:
                self._obs_state = ObsState.READY
                self.push_change_event("obsState", self._obs_state)
        return ([ResultCode.OK], [""])

    def is_End_allowed(self):
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
        """This method invokes End command on SdpSubarray device."""
        if self._defective:
            self.raise_exception_for_defective_device(
                command_name="SdpSubarray.End"
            )

        if not self._defective:
            if self._obs_state != ObsState.IDLE:
                self._obs_state = ObsState.IDLE
                self.push_change_event("obsState", self._obs_state)
        return ([ResultCode.OK], [""])

    def is_Abort_allowed(self):
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
        """This method invokes Abort command on SdpSubarray device."""
        if self._defective:
            self.raise_exception_for_defective_device(
                command_name="SdpSubarray.Abort"
            )

        if self._obs_state != ObsState.ABORTED:
            self._obs_state = ObsState.ABORTED
            self.push_change_event("obsState", self._obs_state)
        return ([ResultCode.OK], [""])

    def is_Restart_allowed(self):
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
        """This method invokes Restart command on SdpSubarray device."""
        if self._defective:
            self.raise_exception_for_defective_device(
                command_name="SdpSubarray.Restart"
            )

        if self._obs_state != ObsState.EMPTY:
            self._obs_state = ObsState.EMPTY
            self.push_change_event("obsState", self._obs_state)
        return ([ResultCode.OK], [""])

    def raise_exception_for_defective_device(self, command_name: str):
        """This method raises an exception if SdpSubarray device is
        defective."""
        self.logger.info(
            "Device is defective, cannot process command completely."
        )
        raise tango.Except.throw_exception(
            "Device is defective.",
            "Device is defective, cannot process command completely.",
            command_name,
            tango.ErrSeverity.ERR,
        )


def main(args=None, **kwargs):
    """
    Runs the HelperSdpSubarray Tango device.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: integer. Exit code of the run method.
    """
    return run((HelperSdpSubarray,), args=args, **kwargs)


if __name__ == "__main__":
    main()
