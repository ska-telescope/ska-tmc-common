"""A module implementing a decorator for Error Propagation."""
from threading import Event
from typing import Callable

from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus


def process_result_and_start_tracker(
    class_instance,
    result: ResultCode,
    message: str,
    task_abort_event: Event,
) -> None:
    """Process the command invocation result and start the tracker thread if
    the command has not failed.

    :param class_instance: The class instance for the command class
    :type class_instance: Class instance
    :param result: Result of invoking the function
    :type result: ResultCode
    :param message: An informational message
    :type message: str
    :param task_abort_event: An event signaling wheather the task has been
        aborted
    :type task_abort_event: Event

    :rtype: None
    """
    if result == ResultCode.FAILED:
        class_instance.update_task_status(result=result, message=message)

        # Check if Timeout is considered for the particular command, default:
        # True
        if class_instance.function_map.get("is_timeout_considered", True):
            # The if else block is to keep backwards compatibility. Once all
            # repositories start using the TimeKeeper class, the block can be
            # replaced with the if part.
            if hasattr(class_instance.component_manager, "timekeeper"):
                class_instance.component_manager.timekeeper.stop_timer()
            else:
                class_instance.component_manager.stop_timer()

        # Check if a cleanup function is defined, execute if present.
        if class_instance.function_map.get("cleanup_function"):
            class_instance.function_map["cleanup_function"]()
    else:
        class_instance.start_tracker_thread(
            class_instance.function_map.get("state_function"),
            class_instance.function_map.get("expected_states"),
            task_abort_event,
            timeout_id=class_instance.timeout_id,
            timeout_callback=class_instance.timeout_callback,
            command_id=class_instance.component_manager.command_id,
            lrcr_callback=(
                class_instance.component_manager.long_running_result_callback
            ),
        )


def error_propagation_decorator(function: Callable) -> Callable:
    """A decorator for implementing error propagation functionality using
    expected states as an input data.

    :rtype: Callable
    """

    def wrapper(*args, **kwargs) -> None:
        """Wrapper method"""
        # Extract class instance from the input arguments
        class_instance = args[0]
        class_instance.logger.debug(
            "Executing the error propagation decorator with: %s, %s",
            args,
            kwargs,
        )

        # If a pre hook is defined in the function map, execute it.
        if class_instance.function_map.get("pre_hook"):
            class_instance.function_map["pre_hook"]()

        # Extract the input argument if present
        argin, is_argin_present = extract_argin(args)

        # Set the task callback and task abort event
        class_instance.task_callback = kwargs["task_callback"]
        task_abort_event = kwargs["task_abort_event"]

        # Set the command to in progress
        class_instance.task_callback(status=TaskStatus.IN_PROGRESS)

        # Set up the data requried for the error propagation functionality
        setup_data(class_instance)

        # Execute the command according to existance of input argument
        if is_argin_present:
            result, message = function(class_instance, argin)
        else:
            result, message = function(class_instance)

        # Process the command result
        process_result_and_start_tracker(
            class_instance,
            result,
            message,
            task_abort_event,
        )

        # If a post hook is defined in the function map, execute it.
        if class_instance.function_map.get("post_hook"):
            class_instance.function_map["post_hook"]()

    return wrapper


def setup_data(class_instance) -> None:
    """Sets up the data required for error propagation.

    :param class_instance: Instance of command class

    :rtype: None
    """
    class_name = class_instance.__class__.__name__
    class_instance.component_manager.command_in_progress = class_name
    class_instance.set_command_id(class_name)


def extract_argin(arguments: tuple) -> tuple[str, bool]:
    """Extracts and returns the argin from the given list of args.

    :param arguments: The input arguments to the function
    :type arguments: Tuple

    :rtype: Tuple[str, bool]
    """
    for element in arguments:
        if isinstance(element, str):
            return element, True

    return "", False
