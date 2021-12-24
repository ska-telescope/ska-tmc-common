from ska_tango_base.control_model import HealthState
from tango import DevState


class Aggregator:
    def __init__(self, cm, logger) -> None:
        self._component_manager = cm
        self._logger = logger

    def aggregate(self):
        raise NotImplementedError("To be defined in the lower level classes")
