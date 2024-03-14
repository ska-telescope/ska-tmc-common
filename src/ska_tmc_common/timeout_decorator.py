"""A module implementing a decorator for Timeout."""
import logging
from operator import methodcaller
from typing import Callable

from ska_ser_logging.configuration import configure_logging
from ska_tango_base.commands import ResultCode

configure_logging()
logger = logging.getLogger(__name__)


def timeout_decorator(
    pre_hook: str = "",
    post_hook: str = "",
) -> Callable:
    """A decorator for implementing timeout functionality.

    :param pre_hook: A function to call at the start of the decorator. Should
        be accessible from the class_instance
    :type pre_hook: str
    :param post_hook: A function to call at the end of the decorator. Should
        be accessible from the class_instance
    :type post_hook: str

    :rtype: Callable
    """

    def timeout_function(function: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> tuple[ResultCode, str]:
            """Wrapper method

            :param args: Optional arguments

            :param kwargs: Optional keyword arguments

            :rtype: Tuple[ResultCode, str]
            """
            class_instance = args[0]
            class_instance.logger.debug(
                "Executing the timeout decorator with: %s, %s", args, kwargs
            )
            if pre_hook:
                methodcaller(pre_hook)(class_instance)

            class_instance.timekeeper.start_timer(
                class_instance.timeout_id,
                class_instance.timeout_callback,
            )
            result = function(*args, **kwargs)
            if post_hook:
                methodcaller(post_hook)(class_instance)

            return result

        return wrapper

    return timeout_function
