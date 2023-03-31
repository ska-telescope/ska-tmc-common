from logging import Logger
from typing import Any, Optional

from ska_tmc_common.enum import TimeoutState


class TimeoutCallback:
    """Callback class for keeping track of timeouts during command executions"""

    def __init__(self, id: str, logger: Logger) -> None:
        """Initialises the timeout state to NOT_OCCURED and id to None"""
        self._id = id
        self.logger = logger
        self._timeout_state = TimeoutState.NOT_OCCURED

    def __call__(
        self, id: str, timeout_state: TimeoutState, **kwargs: Any
    ) -> Optional[ValueError]:
        """Call method for the Callback class that sets the state of the
        timeout.

        :param timeout_state: Enum of TimeoutState class.

        :return: Raises ValueError
        """
        if self._id == id:
            self._timeout_state = timeout_state
        else:
            raise ValueError("The id for the callback is invalid")

    def assert_against_call(
        self, id: str, timeout_state: TimeoutState
    ) -> bool:
        """Assertion method to check if the desired state change has occured."""
        try:
            assert self._id == id
            assert self._timeout_state == timeout_state
            return True
        except AssertionError as e:
            self.logger.exception(e)

        return False
