"""
This module contains a dummy TMC device for testing the integrated TMC.
"""
# pylint: disable=unused-argument

import json
import logging
from logging import Logger
from typing import Any, Optional, Tuple

from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode, SlowCommand
from tango import AttrWriteType

# from tango import DevState
from tango.server import attribute, command

from ska_tmc_common.device_info import (
    DeviceInfo,
    DishDeviceInfo,
    SubArrayDeviceInfo,
)
from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice
from ska_tmc_common.tmc_component_manager import (
    TmcComponent,
    TmcComponentManager,
)

from .constants import (
    ABORT,
    ASSIGN_RESOURCES,
    CONFIGURE,
    END,
    RELEASE_ALL_RESOURCES,
    RELEASE_RESOURCES,
    RESTART,
)

logger = logging.getLogger(__name__)


class DummyComponent(TmcComponent):
    """
    This is a Dummy Component class which monitors and update the device-info.
    """

    def get_device(self, dev_name: str) -> Optional[DeviceInfo]:
        """
        Return the monitored device info by name.

        :param dev_name: name of the device
        :return: the monitored device info
        :rtype: DeviceInfo
        """
        for dev_info in self._devices:
            if dev_info.dev_name == dev_name:
                return dev_info
        return None

    def update_device(self, dev_info: DeviceInfo) -> None:
        """
        Update (or add if missing) Device Information into the list of the
        component.

        :param dev_info: a DeviceInfo object
        """
        if dev_info not in self._devices:
            self._devices.append(dev_info)
        else:
            index = self._devices.index(dev_info)
            self._devices[index] = dev_info


class DummyComponentManager(TmcComponentManager):
    """
    A Dummy component manager for The TMC components.
    """

    def __init__(
        self,
        *args,
        _component: Optional[TmcComponent] = None,
        logger: Logger = logger,
        **kwargs
    ):
        super().__init__(_component=_component, logger=logger, *args, **kwargs)
        self.logger = logger
        self._sample_data = "Default value"

    def set_data(self, value: str) -> Tuple[ResultCode, str]:
        """
        It invokes the SetData Command.

        :param: value
        :return: ResultCode, message
        :rtype: Tuple
        """
        self._sample_data = value
        return ResultCode.OK, ""

    def add_device(self, dev_name: str) -> None:
        """
        Add device to the monitoring loop

        :param dev_name: device name
        :type dev_name: str
        """
        if dev_name is None:
            return

        if "subarray" in dev_name.lower():
            dev_info = SubArrayDeviceInfo(dev_name, False)
        elif "dish/master" in dev_name.lower():
            dev_info = DishDeviceInfo(dev_name, False)
        else:
            dev_info = DeviceInfo(dev_name, False)

        self._component.update_device(dev_info)

    @property
    def sample_data(self) -> str:
        """
        Return the sample data.

        :return: The value of sample data
        :rtype: string
        """
        # import debugpy; debugpy.debug_this_thread()
        return self._sample_data


class DummyTmcDevice(HelperBaseDevice):
    """A dummy TMC device for triggering state changes with a command"""

    class SetDataCommand(SlowCommand):
        """
        This class contains do method which checks the sample data
        """

        def __init__(self, target) -> None:
            super().__init__(target)
            self._component_manager = target.component_manager

        def do(self, value: str) -> Tuple[ResultCode, str]:
            self._component_manager.sample_data = value
            return ResultCode.OK, ""

    def is_SetData_allowed(self) -> bool:
        """
        It checks if the SetData is allowed or not.

        :rtype : bool
        """
        return True

    @command(
        dtype_out="DevVoid",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetData(self, value: Any) -> None:
        """
        It invokes the SetData Command.
        """
        handler = self.get_command_object("SetData")
        handler()


# pylint: disable=attribute-defined-outside-init
class CommandDelayBehaviour(SKABaseDevice):
    """Command Delay Behaviour"""

    def init_device(self):
        super().init_device()
        self._command_delay_info = {
            ASSIGN_RESOURCES: 2,
            CONFIGURE: 2,
            RELEASE_RESOURCES: 2,
            ABORT: 2,
            RESTART: 2,
            RELEASE_ALL_RESOURCES: 2,
            END: 2,
        }

    commandDelayInfo = attribute(dtype=str, access=AttrWriteType.READ)

    def read_commandDelayInfo(self):
        """This method is used to read the attribute value for delay."""

        return json.dumps(self._command_delay_info)

    @command(
        dtype_in=str,
        doc_in="Set Delay",
    )
    def SetDelay(self, command_delay_info: str) -> None:
        """Update delay value"""
        self.logger.info(
            "Setting the Delay value for Csp Subarray from Behaviour class \
                or Sdp Subarray simulator to : %s",
            command_delay_info,
        )
        # set command info
        command_delay_info_dict = json.loads(command_delay_info)
        for key, value in command_delay_info_dict.items():
            self._command_delay_info[key] = value
        self.logger.info("Command Delay Info Set %s", self._command_delay_info)

    @command(
        doc_in="Reset Delay",
    )
    def ResetDelay(self) -> None:
        """Reset Delay to it's default values"""
        self.logger.info(
            "Resetting Command Delays for \
            Csp Subarray or Sdp Simulators"
        )
        # Reset command info
        self._command_delay_info = {
            ASSIGN_RESOURCES: 2,
            CONFIGURE: 2,
            RELEASE_RESOURCES: 2,
            ABORT: 2,
            RESTART: 2,
            RELEASE_ALL_RESOURCES: 2,
            END: 2,
        }
