"""
This module keeps tracks of timeouts during command executions.
"""

from __future__ import annotations

from logging import Logger
from typing import TYPE_CHECKING, Any, Optional

from ska_tmc_common.enum import TimeoutState

if TYPE_CHECKING:
    from ska_tmc_common.command_callback_tracker import CommandCallbackTracker


class TimeoutCallback:
    """Callback class for keeping track of timeouts during command
    executions"""

    def __init__(
        self, timeout_id: str, logger: Logger, command_callback_tracker=None
    ) -> None:
        """Initialises the timeout state to NOT_OCCURED and set the
        timeout_id."""
        self._timeout_id = timeout_id
        self.logger = logger
        self._timeout_state = TimeoutState.NOT_OCCURED
        self.command_callback_tracker = command_callback_tracker
        self._kwargs = {}

    def update_command_callback_tracker(
        self, command_callback_tracker: CommandCallbackTracker
    ):
        """This method updates the instance
        of CommandCallbackTracker class instance.

        Args:
            command_callback_tracker (CommandCallbackTracker):
            CommandCallbackTracker instance.
        """
        self.command_callback_tracker = command_callback_tracker

    def __call__(
        self, timeout_id: str, timeout_state: TimeoutState, **kwargs: Any
    ) -> Optional[ValueError]:
        """Call method for the Callback class that sets the state of the
        timeout.

        :param timeout_id: ID for the callback instance.

        :param timeout_state: Enum of TimeoutState class.

        :raises ValueError: Raises ValueError
        """
        if self._timeout_id == timeout_id:
            self._timeout_state = timeout_state
            for key, value in kwargs.items():
                self._kwargs[key] = value
        else:
            raise ValueError("The id for the callback is invalid")

        if self._timeout_state == TimeoutState.OCCURED:
            if self.command_callback_tracker:
                self.command_callback_tracker.update_timeout_occurred()

    def assert_against_call(
        self, timeout_id: str, timeout_state: TimeoutState, **kwargs: Any
    ) -> bool:
        """
        Assertion method to check if the desired timeout state change
        has occured.
        :return: boolean value
        """
        if timeout_id != self._timeout_id:
            return False

        if timeout_state != self._timeout_state:
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
