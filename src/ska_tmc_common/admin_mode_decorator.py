"""Decorator to check if admin mode is valid to execute the command"""

from functools import wraps
from typing import Any, Callable, Union

from ska_tango_base.control_model import AdminMode


def check_if_admin_mode_offline(
    class_instance: Any, command_name: str
) -> bool:
    """
    Checks if the device is in OFFLINE adminMode. If
        `class_instance._isAdminModeEnabled`
        is False, the check is skipped.

    :param class_instance: The class instance containing the admin mode.
    :type class_instance: Any
    :param command_name: Name of the command being executed.
    :type command_name: str
    :return: Tuple indicating whether the command can proceed (True/False) and
             a message list if any relevant warnings or errors exist.
    :rtype: bool
    """
    # pylint:disable=protected-access
    if not getattr(class_instance, "_isAdminModeEnabled", True):
        return True

    admin_mode = AdminMode(class_instance._admin_mode)
    device_name = class_instance.__class__.__name__

    if admin_mode != AdminMode.ONLINE:
        error_message = (
            f"Device: {device_name} is in {admin_mode.name} "
            f"adminMode. Cannot process command: {command_name}"
            f"Please set adminMode Online and try again"
        )
        if hasattr(class_instance, "logger"):
            class_instance.logger.warning(
                error_message,
            )
        return False

    return True


def admin_mode_check():
    """
    A decorator to check if admin mode is enabled or offline before
    executing the command. If `class_instance._isAdminModeEnabled` is
    False, skips the check and proceeds with the command.

    :return: A wrapped function that performs the admin mode check.
    :rtype: Callable
    """

    def decorator(func: Callable) -> Union[Callable, bool]:
        @wraps(func)
        def wrapper(class_instance: Any, *args: Any, **kwargs: Any) -> bool:
            """
            Wrapper function to perform the admin mode check.

            :param class_instance: The instance of the device class
            :type class_instance: Any
            :param args: Positional arguments for the wrapped function.
            :type args: Any
            :param kwargs: Keyword arguments for the wrapped function.
            :type kwargs: Any
            :return: The result of the wrapped function along with messages.
            :rtype: bool
            """

            def extract_command_name(func_name: str) -> str:
                """
                Extract the command name from a function
                following the pattern 'is_CommandName_allowed'.

                Args:
                    func (Callable): Function to extract
                    the command name from.

                Returns:
                    str: The extracted command name.

                Raises:
                    ValueError: If the function name does
                    not match the expected pattern.
                """
                if func_name.startswith("is_") and func_name.endswith(
                    "_allowed"
                ):

                    command_name = func_name[3:-8]
                    return command_name
                return "Command"

            actual_command_name = extract_command_name(func.__name__)

            admin_mode_enabled = check_if_admin_mode_offline(
                class_instance, actual_command_name
            )

            if not admin_mode_enabled:
                return False

            return func(class_instance, *args, **kwargs)

        return wrapper

    return decorator
