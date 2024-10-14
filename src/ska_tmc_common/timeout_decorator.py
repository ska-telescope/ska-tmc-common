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

        # Set the timeout_id and timeout_callback variables
        # class_instance.set_timer_parameters()

        # Start timer for the command
        if hasattr(class_instance, "timekeeper"):
            class_instance.timekeeper.start_timer(
                class_instance.timeout_id,
                class_instance.timeout_callback,
            )
        else:
            class_instance.component_manager.start_timer(
                class_instance.timeout_id,
                class_instance.component_manager.command_timeout,
                class_instance.timeout_callback,
            )
        # Execute the function with given args and kwargs
        return function(*args, **kwargs)

    return wrapper
