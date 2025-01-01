"""Admin mode check decorator file"""

import os
from functools import wraps
from typing import Any, Callable, List, Optional, Tuple

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import AdminMode

from ska_tmc_common.exceptions import AdminModeException


def check_if_admin_mode_offline(
    class_instance: Any, command_name: str
) -> Tuple[bool, List[ResultCode], List[str]]:
    """
    Checks if the device is in OFFLINE adminMode and raises an exception.

    :param class_instance: The class instance containing the admin mode.
    :type class_instance: Any
    :param command_name: Name of the command being executed.
    :type command_name: str
    :raises AdminModeException: If the device is in OFFLINE adminMode.
    :return: Tuple indicating whether to proceed, ResultCode list, and
             message list if no exception is raised.
    :rtype: Tuple[bool, List[ResultCode], List[str]]
    """
    # pylint:disable=protected-access
    admin_mode = AdminMode(class_instance._admin_mode)
    device_name = class_instance.__class__.__name__
    if admin_mode != AdminMode.ONLINE:
        error_message = (
            f"Device: {device_name} is in {admin_mode.name}"
            + f" adminMode. Cannot process command: {command_name}"
        )
        if hasattr(class_instance, "logger"):
            class_instance.logger.warning(error_message)
        raise AdminModeException(device_name, command_name, error_message)
    return True, [], []


def admin_mode_check(command_name: Optional[str] = None):
    """
    A decorator to check if admin mode is enabled or offline before
    executing the command.

    :param command_name: The name of the command to be checked.
    :type command_name: Optional[str]
    :return: A wrapped function that performs the admin mode check.
    :rtype: Callable
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(
            class_instance: Any, *args: Any, **kwargs: Any
        ) -> Tuple[Any, Any]:
            """
            Wrapper function to perform the admin mode check.

            :param class_instance: The instance of the device class
            :type class_instance: Any
            :param args: Positional arguments for the wrapped function.
            :type args: Any
            :param kwargs: Keyword arguments for the wrapped function.
            :type kwargs: Any
            :raises AdminModeException: If the device is in OFFLINE adminMode.
            :return: The result of the admin mode check
            :rtype: Tuple[Any, Any]
            """
            actual_command_name = command_name or func.__name__

            admin_mode_feature = (
                os.getenv("Admin_Mode_Feature", "false").lower() == "true"
            )

            if admin_mode_feature:
                try:
                    check_if_admin_mode_offline(
                        class_instance, actual_command_name
                    )
                except AdminModeException as exp:
                    raise exp
            else:
                if hasattr(class_instance, "logger"):
                    class_instance.logger.info(
                        "Admin_Mode_Feature is disabled."
                    )

            return func(class_instance, *args, **kwargs)

        return wrapper

    # Allow direct use without parentheses
    if callable(command_name):
        return decorator(command_name)

    return decorator
