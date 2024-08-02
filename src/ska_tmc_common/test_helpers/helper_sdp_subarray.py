# pylint: disable=attribute-defined-outside-init, too-many-ancestors

"""Helper device for SdpSubarray device"""
import json
import logging
import threading
import time
from typing import Tuple

import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tango_base.subarray import SKASubarray
from tango import AttrWriteType, DevState
from tango.server import attribute, command, run

from ska_tmc_common import FaultType
from ska_tmc_common.test_helpers.helper_subarray_device import (
    HelperSubArrayDevice,
)

from .constants import (
    ABORT,
    ASSIGN_RESOURCES,
    CONFIGURE,
    END,
    END_SCAN,
    OFF,
    ON,
    RELEASE_ALL_RESOURCES,
    RELEASE_RESOURCES,
    RESTART,
    SCAN,
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
        # pylint: disable=line-too-long
        self.timers = []
        self._receive_addresses = json.dumps(
            {
                "science_A": {
                    "host": [[0, "192.168.0.1"], [2000, "192.168.0.1"]],
                    "port": [[0, 9000, 1], [2000, 9000, 1]],
                },
                "target:a": {
                    "vis0": {
                        "function": "visibilities",
                        "host": [
                            [
                                0,
                                "proc-pb-test-20220916-00000-test-"
                                + "receive-0.receive.test-sdp",
                            ]
                        ],
                        "port": [[0, 9000, 1]],
                    }
                },
                "calibration:b": {
                    "vis0": {
                        "function": "visibilities",
                        "host": [
                            [
                                0,
                                "proc-pb-test-20220916-00000-test-"
                                + "receive-0.receive.test-sdp",
                            ]
                        ],
                        "port": [[0, 9000, 1]],
                    }
                },
            }
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

        # if receive nodes not present in JSON, SDP Subarray moves to
        # obsState=EMPTY and raises exception
        if input_json["resources"]["receive_nodes"] == 0:
            self.logger.info(
                "Missing receive nodes in the AssignResources input json"
            )
            # Return to the initial obsState
            self._obs_state = initial_obstate
            self.update_device_obsstate(self._obs_state, ASSIGN_RESOURCES)
            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "Missing receive nodes in the AssignResources input json",
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

    def error_message(self, command_name: str):
        """
        Induces a fault for a given command by raising a Tango exception based
        on the specified fault type.

        This method logs the induction of a fault for the provided command and
        raises an exception if the fault type is `LONG_RUNNING_EXCEPTION`.
        The exception message and fault type are
        retrieved from the `defective_params` attribute.

        Parameters:
        command_name (str): The name of the command for
        which the fault is being induced.

        :throws: DevFailed in case of error.
        """
        self.logger.info("Inducing fault for command %s", command_name)

        fault_message = self.defective_params.get(
            "error_message", "Exception occurred"
        )

        raise tango.Except.throw_exception(
            fault_message,
            "Long running exception induced",
            "HelperSdpSubarray.induce_fault()",
            tango.ErrSeverity.ERR,
        )

    def induce_fault(self, command_name: str, command_id: str):
        """
        Induces a fault into the device based on the given parameters.

        :param command_name: The name of the command for which a fault is
            being induced.
        :type command_name: str
        :param command_id: The command id over which the LRCR event is to be
            pushed.
        :type command_id: str


        Example:
            defective_params = json.dumps({"enabled": False,"fault_type":
            FaultType.FAILED_RESULT,"error_message": "Default exception.",
            "result": ResultCode.FAILED,})
            proxy.SetDefective(defective_params)

        Explanation:
        This method induces various types of faults into a device to test its
        robustness and error-handling capabilities.

        - LONG_RUNNING_EXCEPTION:
            A fault type where a failed result will be sent over the
            LongRunningCommandResult attribute in 'delay' amount of time.

        - STUCK_IN_INTERMEDIATE_STATE:
            This fault type makes it such that the device is stuck in the given
            Observation state.
        """
        logger.info("in induce fault method")
        fault_type = self.defective_params.get("fault_type")
        result = self.defective_params.get("result", ResultCode.FAILED)
        fault_message = self.defective_params.get(
            "error_message", "Exception occurred"
        )
        intermediate_state = self.defective_params.get("intermediate_state")

        if fault_type == FaultType.LONG_RUNNING_EXCEPTION:
            thread = threading.Timer(
                self._delay,
                function=self.error_message,
                args=[result, command_name],
                kwargs={"message": fault_message, "command_id": command_id},
            )
            thread.start()

        if fault_type == FaultType.STUCK_IN_INTERMEDIATE_STATE:
            self._obs_state = intermediate_state

    @command()
    def ReleaseAllResources(self):
        """This method invokes ReleaseAllResources command on SdpSubarray
        device."""
        command_id = f"{time.time()}_ReleaseAllResources"
        self.update_command_info(RELEASE_ALL_RESOURCES)
        # need to call induce fault here with some condition
        if self.defective_params["enabled"]:
            logger.info("in induce fault condition")
            return self.induce_fault("ReleaseAllResources", command_id)
        if self._state_duration_info:
            self._follow_state_duration()
        else:
            self._obs_state = ObsState.RESOURCING
            self.update_device_obsstate(self._obs_state, RELEASE_ALL_RESOURCES)
            thread = threading.Timer(
                self._command_delay_info[RELEASE_ALL_RESOURCES],
                self.update_device_obsstate,
                args=[ObsState.EMPTY, RELEASE_ALL_RESOURCES],
            )
            self.timers.append(thread)
            thread.start()
        return None

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
        input_json = json.loads(argin)
        if "scan_id" not in input_json:
            self.logger.info("Missing scan_id in the Scan input json")
            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "Missing scan_id in the Scan input json",
                "SdpSubarry.Configure()",
                tango.ErrSeverity.ERR,
            )
        self._obs_state = ObsState.SCANNING
        self.update_device_obsstate(self._obs_state, SCAN)

    @command()
    def EndScan(self):
        """This method invokes EndScan command on SdpSubarray device."""
        self.update_command_info(END_SCAN)
        self._obs_state = ObsState.READY
        self.update_device_obsstate(self._obs_state, END_SCAN)

    @command()
    def End(self):
        """This method invokes End command on SdpSubarray device."""
        self.update_command_info(END)
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
        self.update_device_obsstate(self._obs_state, ABORT)
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
