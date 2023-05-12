from logging import Logger
from typing import Any, Optional

from ska_tmc_common.enum import ExceptionState


class LRCRCallback:
    """Callback class for keeping track of raised exceptions during command executions"""

    def __init__(self, logger: Logger) -> None:
        """Initialises the exception state to COMMAND_IN_PROGRESS and set the command id."""
        self.command_data = {}
        self.logger = logger
        self._kwargs = {}

    def __call__(
        self,
        command_id: str,
        exception_state: ExceptionState,
        exception_msg,
        **kwargs: Any
    ) -> Optional[ValueError]:
        """Call method for the Callback class that sets the state of the
        exception.

        :param exception_state: Enum of ExceptionState class.

        :return: Raises ValueError
        """
        if command_id in self.command_data:
            self.command_data[command_id]["exception_state"] = exception_state
            self.command_data[command_id]["exception_message"] = exception_msg
            for key, value in kwargs.items():
                self.command_data[command_id][key] = value
        else:
            self.command_data[command_id] = {
                "exception_state": exception_state,
                "exception_message": exception_msg,
            }
            for key, value in kwargs.items():
                self.command_data[command_id][key] = value

    def assert_against_call(
        self, command_id: str, exception_state: ExceptionState, **kwargs: Any
    ) -> bool:
        """Assertion method to check if the desired exception state change has occured."""
        if command_id not in self.command_data:
            return False

        if exception_state != self.command_data[command_id]["exception_state"]:
            self.logger.debug(
                "The actual exception state %s is not equal to asserted exception state %s",
                self.command_data[command_id]["exception_state"],
                exception_state,
            )
            return False

        try:
            for key, value in kwargs.items():
                if self.command_data[command_id][key] != value:
                    return False
        except KeyError as e:
            self.logger.debug(
                "The assertion is invalid as one or more keyword arguments "
                + "are invalid. Error : %s",
                e,
            )
            return False

        return True
