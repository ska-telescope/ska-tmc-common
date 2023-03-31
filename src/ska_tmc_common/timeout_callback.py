import logging
from typing import Any, Optional

from ska_tmc_common.enum import TimeoutState

logger = logging.getLogger(__name__)


class TimeoutCallback:
    """Callback class for keeping track of timeouts during command executions"""

    def __init__(self, id: str) -> None:
        """Initialises the timeout state to NOT_OCCURED and id to None"""
        self._id = id
        self._state = TimeoutState.NOT_OCCURED

    def __call__(
        self, id: str, state: TimeoutState, **kwargs: Any
    ) -> Optional[ValueError]:
        """Call method for the Callback class that sets the state of the
        timeout.

        :param state: Enum of TimeoutState class.
        """
        if self._id == id:
            self._state = state
        else:
            raise ValueError("The id for the callback is invalid")

    def assert_against_call(self, id: str, state: TimeoutState) -> bool:
        """Assertion method to check if the desired state change has occured."""
        if self._id == id:
            if self._state == state:
                return True
            else:
                logger.debug(
                    "The actual state %s is not equal to asserted state %s",
                    self._state,
                    state,
                )
                return False
        else:
            logger.error(
                "The id for callback object is incorrect: %s",
                id,
            )
            return False
