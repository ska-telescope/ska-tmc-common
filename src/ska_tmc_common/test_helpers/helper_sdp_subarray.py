# pylint: disable=attribute-defined-outside-init, too-many-ancestors

"""Helper device for SdpSubarray device"""
import json
import logging
import threading
from typing import Tuple

import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import AdminMode, ObsState
from ska_tango_base.subarray import SKASubarray
from tango import AttrWriteType, DevState
from tango.server import attribute, command, run

from ska_tmc_common import FaultType
from ska_tmc_common.test_helpers.constants import (
    ABORT,
    ASSIGN_RESOURCES,
    CONFIGURE,
    END,
    END_SCAN,
    OFF,
    ON,
    RECEIVE_ADDRESSES_LOW,
    RECEIVE_ADDRESSES_MID,
    RELEASE_ALL_RESOURCES,
    RELEASE_RESOURCES,
    RESTART,
    SCAN,
)
from ska_tmc_common.test_helpers.helper_subarray_device import (
    HelperSubArrayDevice,
)

logger = logging.getLogger(__name__)


# pylint: disable=invalid-name
class HelperSdpSubarray(HelperSubArrayDevice):
    """A  helper SdpSubarray device for triggering state changes with a
    command.
    It can be used to mock SdpSubarray's bahavior to test error propagation
    from SdpSubarray to SdpSubarrayLeafNode in case of command failure"""

    def init_device(self):
        super().init_device()
        self._state = DevState.OFF
        self._admin_mode: AdminMode = AdminMode.ONLINE
        # pylint: disable=line-too-long
        self.timers = []
        self._receive_addresses = (
            RECEIVE_ADDRESSES_LOW
            if "low" in self.dev_name
            else RECEIVE_ADDRESSES_MID
        )

        self.push_change_event("receiveAddresses", self._receive_addresses)

    class InitCommand(SKASubarray.InitCommand):
        """A class for the HelperSubarrayDevice's init_device() "command"."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            :return: ResultCode and message
            """
            super().do()
            self._device.set_change_event("receiveAddresses", True, False)
            self._device.set_change_event("commandCallInfo", True, False)
            return ResultCode.OK, ""

    receiveAddresses = attribute(
        label="Receive addresses",
        dtype=str,
        access=AttrWriteType.READ,
        doc="Host addresses for visibility receive as a JSON string.",
    )
    defective = attribute(dtype=str, access=AttrWriteType.READ)

    delay = attribute(dtype=int, access=AttrWriteType.READ)

    def read_delay(self) -> int:
        """
        This method is used to read the attribute value for delay.
        :return: delay
        """
        return self._delay

    @command(dtype_in=str, doc_in="Set the receive_addresses")
    def SetDirectreceiveAddresses(self, argin: str) -> None:
        """Set the receivedAddresses"""
        self._receive_addresses = argin
        self.push_change_event("receiveAddresses", argin)

    def read_receiveAddresses(self):
        """
        Returns receive addresses.
        :return: receiveAddresses
        """
        return self._receive_addresses

    def read_defective(self) -> str:
        """
        Returns defective status of devices
        :return: defective parameters
        :rtype: str
        """
        return json.dumps(self.defective_params)

    @command()
    def On(self):
        """
        This method simulates On command on SDP Subarray
        """
        self.update_command_info(ON, "")
        self.set_state(DevState.ON)
        self.push_change_event("State", self.dev_state())

    @command()
    def Off(self):
        """
        This method simulates OFF command on SDP Subarray
        """
        self.update_command_info(OFF, "")
        self.set_state(DevState.OFF)
        self.push_change_event("State", self.dev_state())

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format.",
    )
    def AssignResources(self, argin):
        """
        This method simulates AssignResources command on SdpSubarray
        device.
        :raises throw_exception: when input json is wrong
        """
        initial_obstate = self._obs_state
        self.logger.info(
            "Initial obsstate of SdpSubarray for AssignResources command is:"
            + "%s",
            initial_obstate,
        )
        self.update_command_info(ASSIGN_RESOURCES, argin)
        input_json = json.loads(argin)
        if "eb_id" not in input_json["execution_block"]:
            self.logger.info("Missing eb_id in the AssignResources input json")
            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "Missing eb_id in the AssignResources input json",
                "SdpSubarry.AssignResources()",
                tango.ErrSeverity.ERR,
            )

        self._obs_state = ObsState.RESOURCING
        self.update_device_obsstate(self._obs_state, ASSIGN_RESOURCES)

        # if eb_id in JSON is invalid, SDP Subarray
        # remains in obsState=RESOURCING and raises exception
        eb_id = input_json["execution_block"]["eb_id"]
        invalid_eb_id = ("eb-xxx", "eb-test-000")
        if eb_id.startswith(invalid_eb_id):
            self.logger.info("eb_id is invalid")

            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "Invalid eb_id in the AssignResources input json",
                "SdpSubarry.AssignResources()",
                tango.ErrSeverity.ERR,
            )

        if self.defective_params["enabled"]:
            if self.defective_params["fault_type"] == FaultType.SDP_FAULT:
                self._obs_state = ObsState.FAULT
                self.update_device_obsstate(self._obs_state, ASSIGN_RESOURCES)
            elif (
                self.defective_params["fault_type"]
                == FaultType.SDP_BACK_TO_INITIAL_STATE
            ):
                self._obs_state = initial_obstate
                self.update_device_obsstate(self._obs_state, ASSIGN_RESOURCES)

            raise tango.Except.throw_exception(
                "Error ocurred during assign resources",
                self.defective_params["error_message"],
                "SdpSubarry.AssignResources()",
                tango.ErrSeverity.ERR,
            )

        thread = threading.Timer(
            self._command_delay_info[ASSIGN_RESOURCES],
            self.update_device_obsstate,
            args=[ObsState.IDLE, ASSIGN_RESOURCES],
        )
        self.timers.append(thread)
        thread.start()

    @command()
    def ReleaseResources(self):
        """This method invokes ReleaseResources command on SdpSubarray
        device."""
        self.update_command_info(RELEASE_RESOURCES)
        self._obs_state = ObsState.RESOURCING
        self.update_device_obsstate(self._obs_state, RELEASE_RESOURCES)
        thread = threading.Timer(
            self._command_delay_info[RELEASE_RESOURCES],
            self.update_device_obsstate,
            args=[ObsState.IDLE, RELEASE_RESOURCES],
        )
        self.timers.append(thread)
        thread.start()
        self.logger.debug(
            "ReleaseResources command invoked, obsState will transition to"
            + "IDLE, current obsState is %s",
            self._obs_state,
        )

    @command()
    def ReleaseAllResources(self):
        """This method invokes ReleaseAllResources command on SdpSubarray
        device."""
        self.update_command_info(RELEASE_ALL_RESOURCES)
        self._obs_state = ObsState.RESOURCING
        if self.defective_params["enabled"]:
            self._obs_state = ObsState.IDLE
            self.induce_fault()
        self.update_device_obsstate(self._obs_state, RELEASE_ALL_RESOURCES)
        thread = threading.Timer(
            self._command_delay_info[RELEASE_ALL_RESOURCES],
            self.update_device_obsstate,
            args=[ObsState.EMPTY, RELEASE_ALL_RESOURCES],
        )
        self.timers.append(thread)
        thread.start()

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format.",
    )
    def Configure(self, argin):
        """
        This method invokes Configure command on SdpSubarray device.
        :raises throw_exception: when input json is wrong
        """
        self.update_command_info(CONFIGURE, argin)
        input_json = json.loads(argin)
        if "scan_type" not in input_json:
            self.logger.info("Missing scan_type in the Configure input json")
            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "Missing scan_type in the Configure input json",
                "SdpSubarry.Configure()",
                tango.ErrSeverity.ERR,
            )

        self._obs_state = ObsState.CONFIGURING
        self.update_device_obsstate(self._obs_state, CONFIGURE)

        # if scan_type in JSON is invalid , SDP Subarray moves to
        # obsState=IDLE and raises exception
        scan_type = input_json["scan_type"]
        invalid_scan_type = "xxxxxxx_X"
        if scan_type == invalid_scan_type:
            self._obs_state = ObsState.CONFIGURING
            self.update_device_obsstate(self._obs_state, CONFIGURE)
            self.logger.info("Wrong scan_type in the Configure input json")
            self._obs_state = ObsState.IDLE
            thread = threading.Timer(
                1,
                self.update_device_obsstate,
                args=[self._obs_state, CONFIGURE],
            )
            thread.start()
            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "Wrong scan_type in the Configure input json",
                "SdpSubarry.Configure()",
                tango.ErrSeverity.ERR,
            )

        # if scan_type in JSON does not have valid value, SDP Subarray
        # remains in obsState=CONFIGURING and raises exception
        scan_type = input_json["scan_type"]
        invalid_scan_type = "zzzzzzz_Z"
        if scan_type == invalid_scan_type:
            self.logger.info("Wrong scan_type in the Configure input json")
            self._obs_state = ObsState.CONFIGURING
            self.update_device_obsstate(self._obs_state, CONFIGURE)
            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "Wrong scan_type in the Configure input json",
                "SdpSubarry.Configure()",
                tango.ErrSeverity.ERR,
            )
        if self._state_duration_info:
            self._follow_state_duration()
        else:
            self._obs_state = ObsState.CONFIGURING
            self.update_device_obsstate(self._obs_state, CONFIGURE)
            thread = threading.Timer(
                self._command_delay_info[CONFIGURE],
                self.update_device_obsstate,
                args=[ObsState.READY, CONFIGURE],
            )
            self.timers.append(thread)
            thread.start()

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format.",
    )
    def Scan(self, argin):
        """
        This method invokes Scan command on SdpSubarray device.
        :raises throw_exception: when input json is wrong
        """

        self.update_command_info(SCAN, argin)
        if self.defective_params["enabled"]:
            self.logger.info("Scan invoked with defective params")
            self._obs_state = ObsState.READY
            self.induce_fault()
        else:
            self.logger.info("Scan command invoked")
            input_json = json.loads(argin)
            if "scan_id" not in input_json:
                self.logger.info("Missing scan_id in the Scan input json")
                raise tango.Except.throw_exception(
                    "Incorrect input json string",
                    "Missing scan_id in the Scan input json",
                    "SdpSubarry.Configure()",
                    tango.ErrSeverity.ERR,
                )
            thread = threading.Timer(
                self._command_delay_info[SCAN],
                self.update_device_obsstate,
                args=[ObsState.SCANNING, SCAN],
            )
            self.timers.append(thread)
            thread.start()
            self.logger.debug(
                "Scan command invoked, obsState will transition to SCANNING,"
                + "current obsState is %s",
                self._obs_state,
            )

    @command()
    def EndScan(self):
        """This method invokes EndScan command on SdpSubarray device."""

        self.update_command_info(END_SCAN)

        # Allowing stuck in intermediate state defect.
        if self.defective_params["enabled"]:
            self._obs_state = ObsState.SCANNING
            self.induce_fault()
        else:
            thread = threading.Timer(
                self._command_delay_info[END_SCAN],
                self.update_device_obsstate,
                args=[ObsState.READY, END_SCAN],
            )
            self.timers.append(thread)
            thread.start()
            self.logger.debug(
                "EndScan command invoked, obsState will transition to READY,"
                + "current obsState is %s",
                self._obs_state,
            )

    @command()
    def End(self):
        """This method invokes End command on SdpSubarray device."""
        self.update_command_info(END)
        if self.defective_params["enabled"]:
            self._obs_state = ObsState.READY
            self.induce_fault()
        if self._state_duration_info:
            self._follow_state_duration()
        else:
            thread = threading.Timer(
                self._command_delay_info[END],
                self.update_device_obsstate,
                args=[ObsState.IDLE, END],
            )
            self.timers.append(thread)
            thread.start()
            self.logger.debug(
                "End command invoked, obsState will transition to IDLE,"
                + "current obsState is %s",
                self._obs_state,
            )

    @command()
    def Abort(self):
        """This method invokes Abort command on SdpSubarray device."""
        self.update_command_info(ABORT)
        self._obs_state = ObsState.ABORTING
        self.push_change_event("obsState", self._obs_state)
        self.logger.info(
            "Pushing ObsState event for command: %s and obsState: %s",
            "ABORT",
            self._obs_state,
        )
        for timer in self.timers:
            timer.cancel()
        thread = threading.Timer(
            self._command_delay_info[ABORT],
            self.update_device_obsstate,
            args=[ObsState.ABORTED, ABORT],
        )

        thread.start()

    @command()
    def Restart(self):
        """This method invokes Restart command on SdpSubarray device."""
        self.update_command_info(RESTART)
        self._obs_state = ObsState.RESTARTING
        self.update_device_obsstate(self._obs_state, RESTART)
        thread = threading.Timer(
            self._command_delay_info[RESTART],
            self.update_device_obsstate,
            args=[ObsState.EMPTY, RESTART],
        )
        thread.start()
        self.logger.debug(
            "Restart command invoked, obsState will transition to EMPTY,"
            + "current obsState is %s",
            self._obs_state,
        )

    # Note: induce fault mechanism only applicable for releaseAllResoruces
    # if ReleaseAllResources have fault induce enabled it will set obsstate
    # back to Obsstate.IDLE
    def induce_fault(self):
        """
        Induces a fault into the device based on the given parameters.


        Example:

            defective_params = json.dumps({"enabled": False, "fault_type":
            FaultType.FAILED_RESULT, "error_message": "Default exception.",
            "result": ResultCode.FAILED,})
            proxy.SetDefective(defective_params)

        Explanation:

        This method induces various types of faults into a device to test its
        robustness and error-handling capabilities.

        - FAILED_RESULT:
            A fault type where an exception will be raised when command
            invoked with induce fault.

        :raises throw_exception: Raises error to mimic the real device
                                    behavior.
        """
        fault_type = self.defective_params.get("fault_type")
        fault_message = self.defective_params.get(
            "error_message", "Exception occurred"
        )

        if fault_type == FaultType.FAILED_RESULT:
            raise tango.Except.throw_exception(
                fault_message,
                "Exception occurred, command failed",
                "HelperSdpSubarray.induce_fault()",
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
