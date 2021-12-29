from ska_tango_base.base import SKABaseDevice
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import HealthState

# from tango import DevState
from tango.server import command

from ska_tmc_common.op_state_model import TMCOpStateModel
from ska_tmc_common.tmc_component_manager import TmcComponentManager


class DummyComponentManager(TmcComponentManager):
    def __init__(self, op_state_model, logger=None, *args, **kwargs):
        self.logger = logger
        super().__init__(op_state_model, *args, **kwargs)
        self._sample_data = "Default value"

    def set_data(self, value):
        # self.logger.info("New value: %s", value)
        self._sample_data = value
        return (ResultCode.OK, "")

    @property
    def sample_data(self):
        """
        Return the sample data.

        :return: The value of sample data
        :rtype: string
        """
        # import debugpy; debugpy.debug_this_thread()
        return self._sample_data


class DummyDevice(SKABaseDevice):
    """A dummy device for triggering state changes with a command"""

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

    def is_SetData_allowed(self):
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def SetData(self, value):
        self.component_manager
        return [[ResultCode.OK], [""]]
