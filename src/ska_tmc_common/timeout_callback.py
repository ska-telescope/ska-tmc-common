import logging
from enum import IntEnum, unique
from typing import Any, NoReturn, Optional

logger = logging.getLogger(__name__)


@unique
class TimeoutState(IntEnum):
    """
    Enum class for keeping track of timeout state.
    Has 2 values according to the state of timer.

    :NOT_OCCURED: Specifics timer is either running or has been canceled.
    :OCCURED: Specifies the timeout has occured and corresponding method was
        called.
    """

    NOT_OCCURED = 0
    OCCURED = 1


class TimeoutCallback:
    """
    Callback class for keeping track of timeouts during command executions.
    """

    def __init__(self, id: str) -> None:
        """
        Initialises the timeout state to NOT_OCCURED.
        """
        self._id = id
        self._state = TimeoutState.NOT_OCCURED

    def __call__(
        self, id: str, state: TimeoutState, *args: Any, **kwargs: Any
    ) -> Optional[NoReturn]:
        """
        Call method for the Callback class that sets the state of the
        timeout.

        :param state: Enum of TimeoutState class.
        """
        if id == self._id:
            self._state = state
        else:
            raise ValueError(
                f"""Invalid ID for the callback. Expected id was {self._id},
                received id was {id}"""
            )

    def assert_against_call(self, id: str, state: TimeoutState) -> bool:
        """
        Assertion method to check if the desired state change has occured.
        """
        if id != self._id:
            logger.error(
                "The id for callback object is incorrect: %s",
                id,
            )
            return False

        if state != self._state:
            logger.debug(
                "The actual state %s is not equal to asserted state %s",
                self._state,
                state,
            )
            return False

        return True
