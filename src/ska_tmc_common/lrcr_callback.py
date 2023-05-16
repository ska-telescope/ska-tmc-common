"""This module provides a callback to keep track of the
longRunningCommandResult events."""
from logging import Logger
from typing import Any, Optional

from ska_tango_base.commands import ResultCode


class LRCRCallback:
    """Callback class for keeping track of raised exceptions during command executions"""

    def __init__(self, logger: Logger) -> None:
        """Initialises the variables Command Data and the kwargs."""
        self.command_data = {}
        self.logger = logger
        self._kwargs = {}

    def __call__(
        self,
        command_id: str,
        result_code: ResultCode,
        exception_msg: str = "",
        **kwargs: Any,
    ) -> Optional[ValueError]:
        """Call method for the Callback class that sets the state of the
        exception.

        :param command_id: ID of command.

        :param result_code: Enum of ResultCode class.

        :param exception_msg: String of execption message. (Optional)

        :return: Raises ValueError
        """
        self.logger.debug(
            f"Updating command data with command id {command_id} and result "
            f"code {result_code} and kwargs {kwargs}"
        )
        if command_id in self.command_data:
            self.command_data[command_id]["result_code"] = result_code
            self.command_data[command_id]["exception_message"] = exception_msg
            for key, value in kwargs.items():
                self.command_data[command_id][key] = value
        else:
            self.command_data[command_id] = {
                "result_code": result_code,
                "exception_message": exception_msg,
            }
            for key, value in kwargs.items():
                self.command_data[command_id][key] = value

    def assert_against_call(
        self, command_id: str, result_code: ResultCode, **kwargs: Any
    ) -> bool:
        """Assertion method to check if the desired result code change has occured."""
        if command_id not in self.command_data:
            return False

        if result_code != self.command_data[command_id]["result_code"]:
            return False

        try:
            is_valid = [
                self.command_data[command_id][key] == value
                for key, value in kwargs.items()
            ]
            if not all(is_valid):
                return False
        except KeyError as e:
            self.logger.debug(
                "The assertion is invalid as one or more keyword arguments "
                + "are invalid. Error : %s",
                e,
            )
            return False

        return True

    def get_data(self, command_id: str) -> dict:
        """Returns the data for given command id"""
        return self.command_data[command_id]

    def remove_data(self, command_id: str) -> None:
        """Remove command id from command data"""
        removed_data = self.command_data.pop(command_id, None)
        self.logger.info(f"Removed command data {removed_data}")
