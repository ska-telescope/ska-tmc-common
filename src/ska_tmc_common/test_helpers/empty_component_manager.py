"""
This Module contains Empty Component Manager Class for helper subarray devices.
"""
from logging import Logger

from ska_tango_base.base.component_manager import BaseComponentManager

# pylint: disable=abstract-method
# Disabled as this is also a abstract class and has parent class from
# base class


class EmptyComponentManager(BaseComponentManager):
    """
    This is a Dummy Component Manager created for the use of helper devices.
    """

    def __init__(self, *args, logger: Logger, max_workers: int = 1, **kwargs):
        super().__init__(
            logger=logger, max_workers=max_workers, *args, **kwargs
        )

    def start_communicating(self) -> None:
        """This method is not used by TMC."""
        self.logger.info("Start communicating method called")

    def stop_communicating(self) -> None:
        """This method is not used by TMC."""
        self.logger.info("Stop communicating method called")
