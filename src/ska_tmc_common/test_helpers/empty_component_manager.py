from logging import Logger

from ska_tango_base.base.component_manager import BaseComponentManager


class EmptyComponentManager(BaseComponentManager):
    def __init__(self, logger: Logger, max_workers: int = 1, *args, **kwargs):
        super().__init__(
            logger=logger, max_workers=max_workers, *args, **kwargs
        )

    def start_communicating(self) -> None:
        """This method is not used by TMC."""
        self.logger.info("Start communicating method called")
        pass

    def stop_communicating(self) -> None:
        """This method is not used by TMC."""
        self.logger.info("Stop communicating method called")
        pass
