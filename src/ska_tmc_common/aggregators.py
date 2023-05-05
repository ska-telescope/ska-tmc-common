from logging import Logger


class Aggregator:
    def __init__(self, component_manager, logger: Logger) -> None:
        self._component_manager = component_manager
        self._logger = logger

    def aggregate(self) -> NotImplementedError:
        raise NotImplementedError("To be defined in the lower level classes")
