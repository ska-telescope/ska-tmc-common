"""
This module implements the Helper MCCS master leaf node devices for testing
an integrated TMC
"""

from typing import Tuple

from ska_control_model import AdminMode
from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from tango import AttrWriteType
from tango.server import attribute, command

from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice


# pylint: disable=attribute-defined-outside-init,invalid-name
class HelperSDPMasterLeafNode(HelperBaseDevice):
    """A helper MCCS master leafnode device for triggering state
    changes with a command"""

    def init_device(self) -> None:
        super().init_device()
        self._isSubsystemAvailable = True
        self._sdp_controller_admin_mode: AdminMode = AdminMode.OFFLINE

    class InitCommand(SKABaseDevice.InitCommand):
        """A class for the HelperMccsStateDevice's init_device() "command"."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            :return: ResultCode, message
            :rtype:tuple
            """
            super().do()
            self._device.set_change_event("isSubsystemAvailable", True, False)
            self._device.set_change_event(
                "sdpControllerAdminMode", True, False
            )
            self._device.op_state_model.perform_action("component_on")
            return (ResultCode.OK, "")

    sdpControllerAdminMode = attribute(
        dtype=AdminMode,
        doc="Read the SDP controller AdminMode",
        access=AttrWriteType.READ,
    )

    def read_sdpControllerAdminMode(self) -> int:
        """
        Reads the current admin mode of the sdp controller
        :return: admin mode
        """
        return self._sdp_controller_admin_mode

    @command(
        dtype_in=int,
        doc_in="Set AdminMode",
    )
    def SetSdpControllerAdminMode(self, argin: int) -> None:
        """
        Trigger a admin mode change for sdp controller
        :param argin: adminMode enum to set the admin mode.
        :dtype: int
        """
        value = AdminMode(argin)
        if self._sdp_controller_admin_mode != value:
            self._sdp_controller_admin_mode = value
            self.push_change_event(
                "sdpControllerAdminMode", self._sdp_controller_admin_mode
            )
