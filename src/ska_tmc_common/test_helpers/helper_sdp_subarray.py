# pylint: disable=attribute-defined-outside-init, too-many-ancestors
"""Helper device for SdpSubarray device"""
import json
from typing import Tuple

import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tango_base.subarray import SKASubarray
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
        self.push_change_event("receiveAddresses", self._receive_addresses)

    class InitCommand(SKASubarray.InitCommand):
        """A class for the HelperSubarrayDevice's init_device() "command"."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            """
            super().do()
            self._device.set_change_event("receiveAddresses", True, False)
            return ResultCode.OK, ""

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

    @command()
    def On(self):
        """This method invokes On command on SdpSubarray device."""
        if self.dev_state() != DevState.ON:
            self.set_state(DevState.ON)

    def is_Off_allowed(self):
        """
        Check if command `Off` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command()
    def Off(self):
        """This method invokes Off command on SdpSubarray device."""
        if self.dev_state() != DevState.OFF:
            self.set_state(DevState.OFF)

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
    )
    def AssignResources(self, argin):
        """This method invokes AssignResources command on SdpSubarray
        device."""
        if self._defective:
            self._obs_state = ObsState.RESOURCING
            self.push_change_event("obsState", self._obs_state)
            self.raise_exception_for_defective_device(
                command_name="SdpSubarray.AssignResources",
                exception="Device is Defective, \
                    cannot process command completely.",
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

    def is_ReleaseResources_allowed(self):
        """
        Check if command `ReleaseResources` is allowed in the current device
        state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command()
    def ReleaseResources(self):
        """This method invokes ReleaseResources command on SdpSubarray
        device."""
        if self._defective:
            self.raise_exception_for_defective_device(
                command_name="SdpSubarray.ReleaseResources",
                exception="Device is Defective, \
                    cannot process command completely.",
            )

        if not self._defective:
            if self._obs_state != ObsState.EMPTY:
                self._obs_state = ObsState.EMPTY
                self.push_change_event("obsState", self._obs_state)

    def is_ReleaseAllResources_allowed(self):
        """
        Check if command `ReleaseAllResources` is allowed in the current
        device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command()
    def ReleaseAllResources(self):
        """This method invokes ReleaseAllResources command on SdpSubarray
        device."""
        if self._defective:
            self._obs_state = ObsState.RESOURCING
            self.push_change_event("obsState", self._obs_state)
            return

        if self._raise_exception:
            self._obs_state = ObsState.RESOURCING
            self.push_change_event("obsState", self._obs_state)
            self.raise_exception_for_defective_device(
                command_name="SdpSubarray.ReleaseAllResources",
                exception=f"Exception occurred on device: {self.get_name()}",
            )

        if self._obs_state != ObsState.EMPTY:
            self._obs_state = ObsState.EMPTY
            self.push_change_event("obsState", self._obs_state)

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
    )
    def Configure(self, argin):
        """This method invokes Configure command on SdpSubarray device."""
        if self._defective:
            self.raise_exception_for_defective_device(
                command_name="SdpSubarray.Configure",
                exception="Device is Defective, \
                    cannot process command completely.",
            )

        input = json.loads(argin)
        if "scan_type" not in input:
            self.logger.info("Missing scan_type in the Configure input json")
            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "Missing scan_type in the Configure input json",
                "SdpSubarry.Configure()",
                tango.ErrSeverity.ERR,
            )

        if self._obs_state != ObsState.READY:
            self._obs_state = ObsState.READY
            self.push_change_event("obsState", self._obs_state)

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
    )
    def Scan(self, argin):
        """This method invokes Scan command on SdpSubarray device."""
        if self._defective:
            self.raise_exception_for_defective_device(
                command_name="SdpSubarray.Scan",
                exception="Device is Defective, \
                    cannot process command completely.",
            )

        input = json.loads(argin)
        if "scan_id" not in input:
            self.logger.info("Missing scan_id in the Scan input json")
            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "Missing scan_id in the Scan input json",
                "SdpSubarry.Configure()",
                tango.ErrSeverity.ERR,
            )

        if self._obs_state != ObsState.SCANNING:
            self._obs_state = ObsState.SCANNING
            self.push_change_event("obsState", self._obs_state)

    def is_EndScan_allowed(self):
        """
        Check if command `EndScan` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command()
    def EndScan(self):
        """This method invokes EndScan command on SdpSubarray device."""
        if self._defective:
            self.raise_exception_for_defective_device(
                command_name="SdpSubarray.EndScan",
                exception="Device is Defective, \
                    cannot process command completely.",
            )

        if not self._defective:
            if self._obs_state != ObsState.READY:
                self._obs_state = ObsState.READY
                self.push_change_event("obsState", self._obs_state)

    def is_End_allowed(self):
        """
        Check if command `End` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command()
    def End(self):
        """This method invokes End command on SdpSubarray device."""
        if self._defective:
            self.raise_exception_for_defective_device(
                command_name="SdpSubarray.End",
                exception="Device is Defective, \
                    cannot process command completely.",
            )

        if not self._defective:
            if self._obs_state != ObsState.IDLE:
                self._obs_state = ObsState.IDLE
                self.push_change_event("obsState", self._obs_state)

    def is_Abort_allowed(self):
        """
        Check if command `Abort` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command()
    def Abort(self):
        """This method invokes Abort command on SdpSubarray device."""
        if self._defective:
            self.raise_exception_for_defective_device(
                command_name="SdpSubarray.Abort",
                exception="Device is Defective, \
                    cannot process command completely.",
            )

        if self._obs_state != ObsState.ABORTED:
            self._obs_state = ObsState.ABORTED
            self.push_change_event("obsState", self._obs_state)

    def is_Restart_allowed(self):
        """
        Check if command `Restart` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        return True

    @command()
    def Restart(self):
        """This method invokes Restart command on SdpSubarray device."""
        if self._defective:
            self.raise_exception_for_defective_device(
                command_name="SdpSubarray.Restart",
                exception="Device is Defective, \
                    cannot process command completely.",
            )

        if self._obs_state != ObsState.EMPTY:
            self._obs_state = ObsState.EMPTY
            self.push_change_event("obsState", self._obs_state)

    def raise_exception_for_defective_device(
        self, command_name: str, exception: str
    ):
        """This method raises an exception if SdpSubarray device is
        defective."""
        self.logger.info(exception)
        raise tango.Except.throw_exception(
            "Device is Defective.",
            exception,
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