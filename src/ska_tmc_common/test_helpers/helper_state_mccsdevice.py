import json
from typing import List, Literal, Tuple

from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from tango import AttrWriteType
from tango.server import attribute, command

from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice


class HelperMCCSStateDevice(HelperBaseDevice):
    """A generic device for triggering state changes with a command"""

    class InitCommand(SKABaseDevice.InitCommand):
        def do(self) -> Tuple[ResultCode, str]:
            super().do()
            self._device._assigned_resources = "{ }"
            return (ResultCode.OK, "")

    assignedResources = attribute(dtype="DevString", access=AttrWriteType.READ)

    def read_assignedResources(self) -> str:
        return self._device._assigned_resources

    def is_AssignResources_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_in="DevString",
        doc_in="JSON-encoded string with the resources to add to subarray",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def AssignResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        tmpDict = {
            "interface": "https://schema.skatelescope.org/ska-low-mccs-assignedresources/1.0",
            "subarray_beam_ids": [1],
            "station_ids": [[1, 2]],
            "channel_blocks": [3],
        }
        self._assigned_resources = json.dumps(tmpDict)
        return [ResultCode.OK], [""]

    def is_ReleaseResources_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_in="DevString",
        doc_in="JSON-encoded string with the resources to remove from the subarray",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ReleaseResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        tmpDict = {
            "interface": "https://schema.skatelescope.org/ska-low-mccs-assignedresources/1.0",
            "subarray_beam_ids": [],
            "station_ids": [],
            "channel_blocks": [],
        }
        self._assigned_resources = json.dumps(tmpDict)
        return [ResultCode.OK], [""]
