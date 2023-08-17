"""
This module provides a callback mechanism to track command abortion status.
"""
from logging import Logger
from typing import Any, Optional

from ska_tmc_common.enum import CommandState

# pylint: disable=C0301(line-too-long)


class AbortCallback:
    """Callback class for tracking command abortion status.
    executions
    """

    def __init__(self, command_id: str, logger: Logger) -> None:
        """
        Initializes the AbortCallback instance with a specific command ID and logger.

        :param command_id: ID for the callback instance.
        :param logger: Logger instance for logging events.
        """
        self._command_id = command_id
        self.logger = logger
        self.command_state = CommandState.ABORTED
        self._kwargs = {}

    def __call__(
        self, command_id: str, command_state: CommandState, **kwargs: Any
    ) -> Optional[ValueError]:
        """
        Call method for the AbortCallback class that updates the command's abortion status.

        :param command_id: ID for the callback instance.
        :param command_state: Enum of CommandState class representing the command state.
        :param kwargs: Additional keyword arguments.

        :return: Raises ValueError if the provided command_id is invalid.
        """
        if self._command_id == command_id:
            self.command_state = command_state
            for key, value in kwargs.items():
                self._kwargs[key] = value
        else:
            raise ValueError("The id for the callback is invalid")

    def assert_against_call(
        self, command_id: str, command_state: CommandState, **kwargs: Any
    ) -> bool:
        """
        Assertion method to check if the expected command abortion status has been recorded.

        :param command_id: ID for the callback instance.
        :param command_state: Enum of CommandState class representing the command state.
        :param kwargs: Additional keyword arguments.

        :return: True if the provided arguments match the internal recorded state, False otherwise.
        """
        if command_id != self._command_id:
            return False

        if command_state != self.command_state:
            return False

        try:
            for key, value in kwargs.items():
                if self._kwargs[key] != value:
                    return False
        except KeyError as exp_msg:
            self.logger.debug(
                "The assertion is invalid as one or more keyword arguments "
                + "are invalid. Error : %s",
                exp_msg,
            )
            return False

        return True
