import logging
from logging import Logger
from typing import List, Literal, Optional, Tuple

from ska_tango_base.commands import ResultCode, SlowCommand

# from tango import DevState
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


class DummyComponent(TmcComponent):
    def __init__(self, logger: Logger):
        super().__init__(logger)

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
        Update (or add if missing) Device Information into the list of the component.

        :param dev_info: a DeviceInfo object
        """
        if dev_info not in self._devices:
            self._devices.append(dev_info)
        else:
            index = self._devices.index(dev_info)
            self._devices[index] = dev_info


class DummyComponentManager(TmcComponentManager):
    def __init__(
        self,
        _component: Optional[TmcComponent] = None,
        logger: Logger = logger,
        *args,
        **kwargs
    ):
        super().__init__(_component=_component, logger=logger, *args, **kwargs)
        self.logger = logger
        self._sample_data = "Default value"

    def set_data(self, value: str) -> Tuple[ResultCode, str]:
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
        def __init__(self, target):
            self._component_manager = target.component_manager

        def do(self, value: str) -> Tuple[List[ResultCode], str]:
            self._component_manager.sample_data = value
            return [ResultCode.OK], ""

    def is_SetData_allowed(self) -> Literal[True]:
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetData(self, value):
        handler = self.get_command_object("SetData")
        handler()
