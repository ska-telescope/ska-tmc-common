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
        self._kwargs = {}

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
            for key, value in kwargs.items():
                self._kwargs[key] = value
        else:
            raise ValueError("The id for the callback is invalid")

    def assert_against_call(
        self, timeout_id: str, timeout_state: TimeoutState, **kwargs: Any
    ) -> bool:
        """Assertion method to check if the desired timeout state change has occured."""
        if timeout_id != self._timeout_id:
            self.logger.debug("The timeout id is incorrect.")
            return False

        if timeout_state != self._timeout_state:
            self.logger.debug(
                "The actual timeout state %s is not equal to asserted timeout state %s",
                self._timeout_state,
                timeout_state,
            )
            return False

        try:
            for key, value in kwargs.items():
                if self._kwargs[key] != value:
                    return False
        except KeyError as e:
            self.logger.debug(
                "The assertion is invalid as one or more keyword arguments "
                + "are invalid. Error : %s",
                e,
            )
            return False

        return True
