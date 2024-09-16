"""
This module contains a dummy TMC device for testing the integrated TMC.
"""

# pylint: disable=unused-argument

import logging
from logging import Logger
from typing import Optional, Tuple

from ska_tango_base.commands import ResultCode, SlowCommand
from tango.server import command

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

logger = logging.getLogger(__name__)


# pylint: disable=invalid-name
class DummyComponent(TmcComponent):
    """
    This is a Dummy Component class which monitors and update the device-info.
    """

    def get_device(self, device_name: str) -> Optional[DeviceInfo]:
        """
        Return the monitored device info by name.

        :param device_name: name of the device
        :return: the monitored device info
        :rtype: DeviceInfo
        """
        for dev_info in self._devices:
            if dev_info.dev_name == device_name:
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

    def to_dict(self):
        """
        Base method for to_dict method for different nodes
        :raises NotImplementedError: Not implemented error
        """
        raise NotImplementedError("This method must be inherited!")

    def update_device_exception(self, device_info, exception):
        """
        Base method for update_device_exception method for different nodes
        :raises NotImplementedError: Not implemented error
        """
        raise NotImplementedError("This method must be inherited!")


# pylint: disable=redefined-outer-name
# pylint: disable=abstract-method
# Disabled as this is also a abstract class and has parent class from
# base class
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

    def add_device(self, device_name: str) -> None:
        """
        Add device to the monitoring loop

        :param device_name: device name
        :type device_name: str
        """
        if device_name is None:
            return

        if "subarray" in device_name.lower():
            dev_info = SubArrayDeviceInfo(device_name, False)
        elif "dish/master" in device_name.lower():
            dev_info = DishDeviceInfo(device_name, False)
        else:
            dev_info = DeviceInfo(device_name, False)

        self._component.update_device(dev_info)

    @property
    def sample_data(self) -> str:
        """
        Return the sample data.

        :return: The value of sample data
        :rtype: str
        """
        # import debugpy; debugpy.debug_this_thread()
        return self._sample_data


# pylint: enable=redefined-outer-name
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
        :return: boolean value if the SetData is allowed or not
        :rtype : bool
        """
        return True

    @command(
        dtype_out="DevVoid",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetData(self, value) -> None:
        """
        It invokes the SetData Command.
        """
        handler = self.get_command_object("SetData")
        handler()
