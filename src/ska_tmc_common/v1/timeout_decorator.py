"""A module implementing a decorator for Timeout."""
from typing import Callable

from ska_tango_base.commands import ResultCode


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
        # Extract class instance from the input arguments
        class_instance = args[0]
        class_instance.logger.debug(
            "Executing the timeout decorator with: %s, %s", args, kwargs
        )

        # If a pre hook is defined in the function map, execute it.
        if class_instance.function_map.get("pre_hook"):
            class_instance.function_map["pre_hook"]()

        # Start timer for the command execution
        class_instance.timekeeper.start_timer(
            class_instance.timeout_id,
            class_instance.component_manager.command_timeout,
            class_instance.timeout_callback,
        )

        # Execute function with given args and kwargs
        result = function(*args, **kwargs)

        # If a post hook is defined in the function map, execute it.
        if class_instance.function_map.get("post_hook"):
            class_instance.function_map["post_hook"]()

        return result

    return wrapper
