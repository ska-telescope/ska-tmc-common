"""A module implementing a decorator for Timeout."""
import logging
from typing import Callable

from ska_ser_logging.configuration import configure_logging
from ska_tango_base.commands import ResultCode

configure_logging()
logger = logging.getLogger(__name__)


def timeout_decorator(function: Callable) -> Callable:
    """A decorator for implementing timeout functionality.

    :rtype: Callable
    """

    def wrapper(*args, **kwargs) -> tuple[ResultCode, str]:
        """Wrapper method

        :param args: Optional arguments

        :param kwargs: Optional keyword arguments

        :rtype: Tuple[ResultCode, str]
        """
        logger.debug(
            "Executing the timeout decorator with: %s, %s", args, kwargs
        )
        class_instance = args[0]
        class_instance.timekeeper.start_timer(
            class_instance.timeout_id,
            class_instance.timeout_callback,
        )
        return function(*args, **kwargs)

    return wrapper
