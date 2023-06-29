# pylint: disable=attribute-defined-outside-init
"""Helper device for SdpSubarray device"""
import json
import logging

import tango
from ska_tango_base.control_model import HealthState, ObsState
from tango import AttrWriteType, DevState
from tango.server import Device, attribute, command, run


class SdpSubarrayDevice(Device):
    """A  helper SdpSubarray device for triggering state changes with a
    command.
    It can be used to mock SdpSubarray's bahavior to test error propagation
    from SdpSubarray to SdpSubarrayLeafNode in case of command failure"""

    def init_device(self):
        super().init_device()
        self._health_state = HealthState.OK
        self._obs_state = ObsState.EMPTY
        self._defective = False
        self._state = DevState.OFF
        self._receive_addresses = '{"science_A":{"host":[[0,"192.168.0.1"], \
        [2000,"192.168.0.1"]],"port":[[0,9000,1],[2000,9000,1]]}}'
        self.set_change_event("State", True, False)
        self.set_change_event("obsState", True, False)
        self.set_change_event("healthState", True, False)
        self.set_change_event("receiveAddresses", True, False)
        self.logger = logging.getLogger(__name__)

    defective = attribute(dtype=bool, access=AttrWriteType.READ)

    healthState = attribute(
        label="Health state",
        dtype=HealthState,
        access=AttrWriteType.READ,
        doc="Device health state",
    )

    obsState = attribute(
        label="Observing state",
        dtype=ObsState,
        access=AttrWriteType.READ,
        doc="The device observing state.",
    )

    receiveAddresses = attribute(
        label="Receive addresses",
        dtype=str,
        access=AttrWriteType.READ,
        doc="Host addresses for visibility receive as a JSON string.",
    )

    def read_defective(self) -> bool:
        """
        This method is used to read the value of the attribute defective
        :rtype:bool
        """
        return self._defective

    def read_receiveAddresses(self):
        """Returns receive addresses."""
        return self._receive_addresses

    def read_healthState(self):
        """Returns health state of SdpSubarray."""
        return self._health_state

    def read_obsState(self):
        """Returns obsState of SdpSubarray."""
        return self._obs_state

    @command(
        dtype_in=bool,
        doc_in="Set Defective",
    )
    def SetDefective(self, value: bool) -> None:
        """
        Trigger defective change
        :rtype: bool
        """
        # self.logger.info("Setting the defective value to : %s", value)
        self._defective = value

    @command(
        dtype_in=int,
        doc_in="Set ObsState",
    )
    def SetDirectObsState(self, argin):
        """
        Trigger a ObsState change
        """
        # import debugpy; debugpy.debug_this_thread()
        value = ObsState(argin)
        if self._obs_state != value:
            self._obs_state = value
            self.push_change_event("obsState", self._obs_state)

    @command(
        dtype_in="DevState",
        doc_in="state to assign",
    )
    def SetDirectState(self, argin):
        """
        Trigger a DevState change
        """
        # import debugpy; debugpy.debug_this_thread()
        if self.dev_state() != argin:
            self.set_state(argin)
            self.push_change_event("State", self.dev_state())

    @command(
        dtype_in=int,
        doc_in="state to assign",
    )
    def SetDirectHealthState(self, argin):
        """
        Trigger a HealthState change
        """
        # import debugpy; debugpy.debug_this_thread()
        # # pylint: disable=E0203
        value = HealthState(argin)
        if self._health_state != value:
            self._health_state = HealthState(argin)
            self.push_change_event("healthState", self._health_state)

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
            self.raise_exception_for_defective_device()

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
            self.raise_exception_for_defective_device()

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
            self.raise_exception_for_defective_device()

        if not self._defective:
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
            self.raise_exception_for_defective_device()

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
            self.raise_exception_for_defective_device()

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
            self.raise_exception_for_defective_device()

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
            self.raise_exception_for_defective_device()

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
            self.raise_exception_for_defective_device()

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
            self.raise_exception_for_defective_device()

        if self._obs_state != ObsState.EMPTY:
            self._obs_state = ObsState.EMPTY
            self.push_change_event("obsState", self._obs_state)

    def raise_exception_for_defective_device(self):
        """This method raises an exception if SdpSubarray device is
        defective."""
        self.logger.info(
            "Device is Defective, cannot process command completely."
        )
        raise tango.Except.throw_exception(
            "Device is Defective.",
            "Device is Defective, cannot process command completely.",
            "SdpSubarry.AssignResources",
            tango.ErrSeverity.ERR,
        )


def main(args=None, **kwargs):
    """
    Runs the SdpSubarrayDevice Tango device.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: integer. Exit code of the run method.
    """
    return run((SdpSubarrayDevice,), args=args, **kwargs)


if __name__ == "__main__":
    main()
