from ska_tango_base.base import SKABaseDevice
from ska_tango_base.commands import ResultCode, SlowCommand
from ska_tango_base.control_model import HealthState

# from tango import DevState
from tango.server import command

from ska_tmc_common import (
    DeviceInfo,
    SubArrayDeviceInfo,
    TmcComponent,
    TmcComponentManager,
)


class DummyComponent(TmcComponent):
    def __init__(self, logger):
        super().__init__(logger)

    def get_device(self, dev_name):
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

    def update_device(self, dev_info):
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
    def __init__(self, _component=None, logger=None, *args, **kwargs):
        super().__init__(_component, logger, *args, **kwargs)
        self.logger = logger
        self._sample_data = "Default value"

    def set_data(self, value):
        self._sample_data = value
        return (ResultCode.OK, "")

    def add_device(self, dev_name):
        """
        Add device to the monitoring loop

        :param dev_name: device name
        :type dev_name: str
        """
        if dev_name is None:
            return

        if "subarray" in dev_name.lower():
            dev_info = SubArrayDeviceInfo(dev_name, False)
        else:
            dev_info = DeviceInfo(dev_name, False)

        self.component.update_device(dev_info)

    @property
    def sample_data(self):
        """
        Return the sample data.

        :return: The value of sample data
        :rtype: string
        """
        # import debugpy; debugpy.debug_this_thread()
        return self._sample_data


class DummyTmcDevice(SKABaseDevice):
    """A dummy TMC device for triggering state changes with a command"""

    def init_device(self):
        super().init_device()
        self._health_state = HealthState.OK

    class InitCommand(SKABaseDevice.InitCommand):
        def do(self):
            super().do()
            self._device.set_change_event("State", True, False)
            self._device.set_change_event("healthState", True, False)
            return (ResultCode.OK, "")

    def create_component_manager(self):
        cm = DummyComponentManager(
            logger=self.logger,
            max_workers=None,
            communication_state_callback=None,
            component_state_callback=None,
        )
        return cm

    class SetDataCommand(SlowCommand):
        def __init__(self, target):
            self._component_manager = target.component_manager

        def do(self, value):
            self._component_manager.sample_data = value
            return [[ResultCode.OK], ""]

    def is_SetData_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetData(self, value):
        handler = self.get_command_object("SetData")
        handler()
