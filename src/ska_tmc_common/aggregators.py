"""
Abstract class for Aggregators
"""
from logging import Logger


class Aggregator:
    """
    Abstract class for Aggregators
    """

    def __init__(self, component_manager, logger: Logger) -> None:
        self._component_manager = component_manager
        self._logger = logger

    def aggregate(self) -> NotImplementedError:
        """
        Abstract method for Aggregators
        """
        raise NotImplementedError("To be defined in the lower level classes")
