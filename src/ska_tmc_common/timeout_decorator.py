"""A module implementing a decorator for Timeout."""
from typing import Callable

from ska_tango_base.commands import ResultCode


def timeout_decorator(fn: Callable) -> Callable:
    """A decorator for implementing timeout functionality."""

    def wrapper(*args, **kwargs) -> tuple[ResultCode, str]:
        """Wrapper method"""
        class_instance = args[0]
        class_instance.timekeeper.start_timer(
            class_instance.timeout_id,
            class_instance.timeout_callback,
        )
        return fn(*args, **kwargs)

    return wrapper
