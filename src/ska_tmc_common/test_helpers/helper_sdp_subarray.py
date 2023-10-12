# pylint: disable=attribute-defined-outside-init, too-many-ancestors
"""Helper device for SdpSubarray device"""
import json
import logging
import threading
import time
from time import sleep
from typing import Tuple

import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tango_base.subarray import SKASubarray
from tango import AttrWriteType, DevState
from tango.server import attribute, command, run

from ska_tmc_common import CommandNotAllowed, FaultType, HelperSubArrayDevice

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


class HelperSdpSubarray(HelperSubArrayDevice):
    """A  helper SdpSubarray device for triggering state changes with a
    command.
    It can be used to mock SdpSubarray's bahavior to test error propagation
    from SdpSubarray to SdpSubarrayLeafNode in case of command failure"""

    def init_device(self):
        super().init_device()
        self._delay = 2
        self._obs_state = ObsState.EMPTY
        self._defective = json.dumps(
            {
                "enabled": False,
                "fault_type": FaultType.FAILED_RESULT,
                "error_message": "Default exception.",
                "result": ResultCode.FAILED,
            }
        )
        self.defective_params = json.loads(self._defective)
        self._pointing_offsets = []
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
            self._device.set_change_event("healthState", True, False)
            self._device.set_change_event("pointing_offsets", True, False)
            self._device.set_change_event(
                "longRunningCommandResult", True, False
            )
            self._device.set_change_event("commandCallInfo", True, False)
            return ResultCode.OK, ""

    receiveAddresses = attribute(
        label="Receive addresses",
        dtype=str,
        access=AttrWriteType.READ,
        doc="Host addresses for visibility receive as a JSON string.",
    )

    pointingOffsets = attribute(dtype=str, access=AttrWriteType.READ_WRITE)

    defective = attribute(dtype=str, access=AttrWriteType.READ)

    delay = attribute(dtype=int, access=AttrWriteType.READ)

    def read_delay(self) -> int:
        """This method is used to read the attribute value for delay."""
        return self._delay

    def read_pointingOffsets(self) -> str:
        """This method is used to read the attribute value for
        pointing_offsets from QueueConnector SDP device."""
        return json.dumps(self._pointing_offsets)

    def write_pointingOffsets(self, value: str) -> None:
        """This method is used to write the attribute value for
        pointing_offsets for testing purpose.

        :param value: A list in json format containing cross elevation and \
            elevation offsets along with scan id / time.
        """
        pointing_offsets_data = json.loads(value)
        dish_id = pointing_offsets_data[0]
        cross_elevation = pointing_offsets_data[3]
        elevation_offset = pointing_offsets_data[5]
        self.logger.info(
            "The pointing corrections for cross elevation and elevation are: "
            + "%s, %s",
            cross_elevation,
            elevation_offset,
        )
        self._pointing_offsets = [dish_id, cross_elevation, elevation_offset]
        # wait for sometime to reflect it on SDPLN attribute
        sleep(5)
        self.set_pointing_offsets()

    def read_receiveAddresses(self):
        """Returns receive addresses."""
        return self._receive_addresses

    def read_defective(self) -> str:
        """
        Returns defective status of devices

        :rtype: str
        """
        return self._defective

    def set_pointing_offsets(self):
        """ "
        This method is to push the change event for pointing_offsets attribute
        """
        self.push_change_event("pointingOffsets", self._pointing_offsets)

    def push_command_result(
        self, result: ResultCode, command: str, exception: str = ""
    ) -> None:
        """Push long running command result event for given command.

        :params:

        result: The result code to be pushed as an event
        dtype: ResultCode

        command: The command name for which the event is being pushed
        dtype: str

        exception: Exception message to be pushed as an event
        dtype: str
        """
        command_id = f"{time.time()}-{command}"
        self.logger.info(
            "The command_id is %s and the ResultCode is %s", command_id, result
        )
        if exception:
            command_result = (command_id, exception)
            self.push_change_event("longRunningCommandResult", command_result)
        command_result = (command_id, json.dumps(result))
        self.push_change_event("longRunningCommandResult", command_result)

    def push_obs_state_event(self, obs_state: ObsState):
        """Place holder method. This method will be implemented in the child
        classes."""
        self.push_change_event("obsState", self._obs_state)

    def update_device_obsstate(self, obs_state: ObsState):
        """Updates the device obsState"""
        with tango.EnsureOmniThread():
            self._obs_state = obs_state
            time.sleep(0.1)
            self.push_obs_state_event(self._obs_state)

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

    @command()
    def On(self):
        self.update_command_info(ON, "")
        if self.defective_params["enabled"]:
            self.induce_fault(
                "On",
            )
        else:
            self.set_state(DevState.ON)
            self.push_change_event("State", self.dev_state())
            self.push_command_result(ResultCode.OK, "On")

    def is_Off_allowed(self) -> bool:
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                logger.info("Device is defective, cannot process command.")
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("Off Command is allowed")
        return True

    @command()
    def Off(self):
        self.update_command_info(OFF, "")
        if self.defective_params["enabled"]:
            self.induce_fault(
                "Off",
            )
        else:
            self.set_state(DevState.OFF)
            self.push_change_event("State", self.dev_state())
            self.push_command_result(ResultCode.OK, "Off")

    def is_AssignResources_allowed(self):
        """
        Check if command `AssignResources` is allowed in the current device
        state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("AssignResources Command is allowed")
        return True

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format.",
    )
    def AssignResources(self, argin):
        """This method invokes AssignResources command on SdpSubarray
        device."""
        self.update_command_info(ASSIGN_RESOURCES, argin)
        input = json.loads(argin)
        if "eb_id" not in input["execution_block"]:
            self.logger.info("Missing eb_id in the AssignResources input json")
            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "Missing eb_id in the AssignResources input json",
                "SdpSubarry.AssignResources()",
                tango.ErrSeverity.ERR,
            )

        if self.defective_params["enabled"]:
            self.induce_fault(
                "AssignResources",
            )
        else:
            self._obs_state = ObsState.RESOURCING
            self.push_obs_state_event(self._obs_state)
            thread = threading.Timer(
                self._command_delay_info[ASSIGN_RESOURCES],
                self.update_device_obsstate,
                args=[ObsState.IDLE],
            )
            thread.start()
            self.push_command_result(ResultCode.OK, "AssignResources")

    def is_ReleaseResources_allowed(self):
        """
        Check if command `ReleaseResources` is allowed in the current device
        state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("ReleaseResource Command is allowed")
        return True

    @command()
    def ReleaseResources(self):
        """This method invokes ReleaseResources command on SdpSubarray
        device."""
        self.update_command_info(RELEASE_RESOURCES)
        if self.defective_params["enabled"]:
            self.induce_fault(
                "ReleaseResources",
            )
        else:
            self._obs_state = ObsState.RESOURCING
            self.push_obs_state_event(self._obs_state)
            thread = threading.Timer(
                self._command_delay_info[RELEASE_RESOURCES],
                self.update_device_obsstate,
                args=[ObsState.IDLE],
            )
            thread.start()
            self.logger.debug(
                "ReleaseResources invoked obsstate is transition \
                          to Resourcing"
            )
            self.push_command_result(ResultCode.OK, "ReleaseResources")

    def is_ReleaseAllResources_allowed(self):
        """
        Check if command `ReleaseAllResources` is allowed in the current
        device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("ReleaseAllResources Command is allowed")
        return True

    @command()
    def ReleaseAllResources(self):
        """This method invokes ReleaseAllResources command on SdpSubarray
        device."""
        self.update_command_info(RELEASE_ALL_RESOURCES)
        if self.defective_params["enabled"]:
            self.induce_fault(
                "ReleaseAllResources",
            )
        else:
            self._obs_state = ObsState.RESOURCING
            self.push_obs_state_event(self._obs_state)
            thread = threading.Timer(
                self._command_delay_info[RELEASE_ALL_RESOURCES],
                self.update_device_obsstate,
                args=[ObsState.EMPTY],
            )
            thread.start()
            self.push_command_result(ResultCode.OK, "ReleaseAllResources")

    def is_Configure_allowed(self):
        """
        Check if command `Configure` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("Configure Command is allowed")
        return True

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format.",
    )
    def Configure(self, argin):
        """This method invokes Configure command on SdpSubarray device."""
        self.update_command_info(CONFIGURE, argin)
        input = json.loads(argin)
        if "scan_type" not in input:
            self.logger.info("Missing scan_type in the Configure input json")
            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "Missing scan_type in the Configure input json",
                "SdpSubarry.Configure()",
                tango.ErrSeverity.ERR,
            )

        if self.defective_params["enabled"]:
            self.induce_fault(
                "Configure",
            )
        else:
            if self._state_duration_info:
                self._follow_state_duration()
            else:
                self._obs_state = ObsState.CONFIGURING
                self.push_obs_state_event(self._obs_state)
                thread = threading.Timer(
                    self._command_delay_info[CONFIGURE],
                    self.update_device_obsstate,
                    args=[ObsState.READY],
                )
                thread.start()
                self.push_command_result(ResultCode.OK, "Configure")

    def is_Scan_allowed(self):
        """
        Check if command `Scan` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("Scan Command is allowed")
        return True

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format.",
    )
    def Scan(self, argin):
        """This method invokes Scan command on SdpSubarray device."""
        self.update_command_info(SCAN, argin)
        input = json.loads(argin)
        if "scan_id" not in input:
            self.logger.info("Missing scan_id in the Scan input json")
            raise tango.Except.throw_exception(
                "Incorrect input json string",
                "Missing scan_id in the Scan input json",
                "SdpSubarry.Configure()",
                tango.ErrSeverity.ERR,
            )
        if self.defective_params["enabled"]:
            self.induce_fault(
                "Scan",
            )
        else:
            self._obs_state = ObsState.SCANNING
            self.push_obs_state_event(self._obs_state)
            self.push_command_result(ResultCode.OK, "Scan")

    def is_EndScan_allowed(self):
        """
        Check if command `EndScan` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        self.logger.info("EndScan Command is allowed")
        return True

    @command()
    def EndScan(self):
        """This method invokes EndScan command on SdpSubarray device."""
        self.update_command_info(END_SCAN)
        if self.defective_params["enabled"]:
            self.induce_fault(
                "EndScan",
            )
        else:
            self._obs_state = ObsState.READY
            self.push_obs_state_event(self._obs_state)
            self.push_command_result(ResultCode.OK, "EndScan")

    def is_End_allowed(self):
        """
        Check if command `End` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        return True

    @command()
    def End(self):
        """This method invokes End command on SdpSubarray device."""
        self.update_command_info(END)
        if self.defective_params["enabled"]:
            self.induce_fault(
                "End",
            )
        else:
            if self._state_duration_info:
                self._follow_state_duration()
            else:
                self._obs_state = ObsState.CONFIGURING
                self.push_obs_state_event(self._obs_state)
                thread = threading.Timer(
                    self._command_delay_info[END],
                    self.update_device_obsstate,
                    args=[ObsState.IDLE],
                )
                thread.start()
                self.logger.debug(
                    "END invoked obsstate is transition \
                        to Configuring"
                )
                self.push_command_result(ResultCode.OK, "End")

    def is_Abort_allowed(self):
        """
        Check if command `Abort` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        return True

    @command()
    def Abort(self):
        """This method invokes Abort command on SdpSubarray device."""
        self.update_command_info(ABORT)
        if self.defective_params["enabled"]:
            self.induce_fault(
                "Abort",
            )
        else:
            self._obs_state = ObsState.ABORTING
            self.push_obs_state_event(self._obs_state)
            thread = threading.Timer(
                self._command_delay_info[ABORT],
                self.update_device_obsstate,
                args=[ObsState.ABORTED],
            )
            thread.start()
            self.push_command_result(ResultCode.OK, "Abort")

    def is_Restart_allowed(self):
        """
        Check if command `Restart` is allowed in the current device state.

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        if self.defective_params["enabled"]:
            if (
                self.defective_params["fault_type"]
                == FaultType.COMMAND_NOT_ALLOWED
            ):
                self.logger.info(
                    "Device is defective, cannot process command."
                )
                raise CommandNotAllowed(self.defective_params["error_message"])
        return True

    @command()
    def Restart(self):
        """This method invokes Restart command on SdpSubarray device."""
        self.update_command_info(RESTART)
        if self.defective_params["enabled"]:
            self.induce_fault(
                "Restart",
            )
        else:
            self._obs_state = ObsState.RESTARTING
            self.push_obs_state_event(self._obs_state)
            thread = threading.Timer(
                self._command_delay_info[RESTART],
                self.update_device_obsstate,
                args=[ObsState.EMPTY],
            )
            thread.start()
            self.logger.debug(
                "Restarting invoked obsstate is transition \
                          to RESTARTING"
            )
            self.push_command_result(ResultCode.OK, "Restart")


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
