from ska_tango_base.base import SKABaseDevice
from ska_tango_base.commands import ResponseCommand, ResultCode
from ska_tango_base.control_model import HealthState

# from tango import DevState
from tango.server import command

from ska_tmc_common.device_info import DeviceInfo, SubArrayDeviceInfo
from ska_tmc_common.op_state_model import TMCOpStateModel
from ska_tmc_common.tmc_component_manager import (
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
        for devInfo in self._devices:
            if devInfo.dev_name == dev_name:
                return devInfo
        return None

    def update_device(self, devInfo):
        """
        Update (or add if missing) Device Information into the list of the component.

        :param devInfo: a DeviceInfo object
        """
        if devInfo not in self._devices:
            self._devices.append(devInfo)
        else:
            index = self._devices.index(devInfo)
            self._devices[index] = devInfo


class DummyComponentManager(TmcComponentManager):
    def __init__(
        self, op_state_model, logger=None, component=None, *args, **kwargs
    ):
        super().__init__(op_state_model, component, logger, *args, **kwargs)
        self.logger = logger
        self._sample_data = "Default value"

    def set_data(self, value):
        # self.logger.info("New value: %s", value)
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
            devInfo = SubArrayDeviceInfo(dev_name, False)
        else:
            devInfo = DeviceInfo(dev_name, False)

        self.component.update_device(devInfo)

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
            device = self.target
            device.set_change_event("State", True, False)
            device.set_change_event("healthState", True, False)
            return (ResultCode.OK, "")

    def create_component_manager(self):
        self.op_state_model = TMCOpStateModel(
            logger=self.logger, callback=super()._update_state
        )

        cm = DummyComponentManager(
            self.op_state_model, self.obs_state_model, self.logger
        )
        return cm

    class SetDataCommand(ResponseCommand):
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
