from typing import Literal

from ska_tango_base.commands import ResultCode
from tango.server import command

from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice


class HelperSubarrayLeafDevice(HelperBaseDevice):
    """A device exposing commands and attributes of the Subarray Leaf Nodes devices."""

    def is_AssignResources_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format consists of receptorIDList.",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def AssignResources(self, argin):
        if not self._defective:
            self.logger.info("AssignResource completed.")
            return [ResultCode.OK], [""]
        else:
            return [ResultCode.FAILED], [
                "Device is Defective, cannot process command."
            ]

    def is_Configure_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Configure(self, argin):
        if not self._defective:
            self.logger.info("Configure completed.")
            return [ResultCode.OK], [""]
        else:
            return [ResultCode.FAILED], [
                "Device is Defective, cannot process command."
            ]

    def is_Scan_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Scan(self, argin):
        if not self._defective:
            self.logger.info("Scan completed.")
            return [ResultCode.OK], [""]
        else:
            return [ResultCode.FAILED], [
                "Device is Defective, cannot process command."
            ]

    def is_EndScan_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def EndScan(self):
        if not self._defective:
            self.logger.info("EndScan completed.")
            return [ResultCode.OK], [""]
        else:
            return [ResultCode.FAILED], [
                "Device is Defective, cannot process command."
            ]

    def is_End_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def End(self):
        if not self._defective:
            self.logger.info("End completed.")
            return [ResultCode.OK], [""]
        else:
            return [ResultCode.FAILED], [
                "Device is Defective, cannot process command."
            ]

    def is_GoToIdle_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def GoToIdle(self):
        if not self._defective:
            self.logger.info("GoToIdle completed.")
            return [ResultCode.OK], [""]
        else:
            return [ResultCode.FAILED], [
                "Device is Defective, cannot process command."
            ]

    def is_Abort_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Abort(self):
        self.logger.info("Abort completed.")
        return [ResultCode.OK], [""]

    def is_ObsReset_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ObsReset(self):
        if not self._defective:
            self.logger.info("ObsReset completed.")
            return [ResultCode.OK], [""]
        else:
            return [ResultCode.FAILED], [
                "Device is Defective, cannot process command."
            ]

    def is_Restart_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Restart(self):
        self.logger.info("Restart completed.")
        return [ResultCode.OK], [""]

    def is_ReleaseAllResources_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ReleaseAllResources(self):
        if not self._defective:
            self.logger.info("ReleaseAllResources completed")
            return [ResultCode.OK], [""]
        else:
            return [ResultCode.FAILED], [
                "Device is Defective, cannot process command."
            ]

    def is_ReleaseResources_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format consists of receptorIDList.",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ReleaseResources(self, argin):
        if not self._defective:
            self.logger.info("ReleaseResources completed.")
            return [ResultCode.OK], [""]
        else:
            return [ResultCode.FAILED], [
                "Device is Defective, cannot process command."
            ]
