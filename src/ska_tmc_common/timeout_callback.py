from logging import Logger
from typing import Any, Optional

from ska_tmc_common.enum import TimeoutState


class TimeoutCallback:
    """Callback class for keeping track of timeouts during command executions"""

    def __init__(self, timeout_id: str, logger: Logger) -> None:
        """Initialises the timeout state to NOT_OCCURED and set the timeout_id."""
        self._timeout_id = timeout_id
        self.logger = logger
        self._timeout_state = TimeoutState.NOT_OCCURED

    def __call__(
        self, timeout_id: str, timeout_state: TimeoutState, **kwargs: Any
    ) -> Optional[ValueError]:
        """Call method for the Callback class that sets the state of the
        timeout.

        :param timeout_state: Enum of TimeoutState class.

        :return: Raises ValueError
        """
        if self._timeout_id == timeout_id:
            self._timeout_state = timeout_state
        else:
            raise ValueError("The id for the callback is invalid")

    def assert_against_call(
        self, timeout_id: str, timeout_state: TimeoutState
    ) -> bool:
        """Assertion method to check if the desired state change has occured."""
        try:
            assert self._timeout_id == timeout_id
            assert self._timeout_state == timeout_state
            return True
        except AssertionError as e:
            self.logger.exception(e)

        return False
