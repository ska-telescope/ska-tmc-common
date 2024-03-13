"""A module implementing a decorator for Error Propagation."""
from threading import Event
from typing import Callable, Optional

from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus


def process_result_and_start_tracker(
    class_instance,
    result: ResultCode,
    message: str,
    expected_states: list,
    task_abort_event: Event,
    is_timeout_considered: bool,
    cleanup_function: Optional[Callable] = None,
) -> None:
    """Process the command invocation result and start the tracker thread if
    the command has not failed.

    :param class_instance: The class instance for the command class
    :type class_instance: Class instance
    :param result: Result of invoking the function
    :type result: ResultCode
    :param message: An informational message
    :type message: str
    :param expected_states: The list of states that the device is expected to
        achieve during the course of the command.
    :type expected_states: List
    :param task_abort_event: An event signaling wheather the task has been
        aborted
    :type task_abort_event: Event
    :param is_timeout_considered: A bool representing wheather timeout is
        implemented
    :type is_timeout_considered: bool
    :param cleanup_function: Optional function that cleans up the device after
        command failure
    :type cleanup_function: Optional[Callable]

    :rtype: None
    """
    if result == ResultCode.FAILED:
        class_instance.update_task_status(result=result, message=message)
        if is_timeout_considered:
            class_instance.timekeeper.stop_timer()
        if cleanup_function:
            cleanup_function()
    else:
        class_instance.start_tracker_thread(
            class_instance.component_manager.get_subarray_obsstate,
            expected_states,
            task_abort_event,
            timeout_id=class_instance.timeout_id,
            timeout_callback=class_instance.timeout_callback,
            command_id=class_instance.component_manager.command_id,
            lrcr_callback=(
                class_instance.component_manager.long_running_result_callback
            ),
        )


def error_propagation_decorator(
    expected_states: list,
    is_timeout_considered: bool = True,
    cleanup_function: Optional[Callable] = None,
) -> Callable:
    """A decorator for implementing error propagation functionality using
    expected states as an input data.

    :param expected_states: The list of states that the device is expected to
        achieve during the course of the command.
    :type expected_states: List
    :param is_timeout_considered: A bool representing wheather timeout is
        implemented
    :type is_timeout_considered: bool
    :param cleanup_function: Optional function that cleans up the device after
        command failure
    :type cleanup_function: Optional[Callable]

    :rtype: Callable
    """

    def error_propagation(fn: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> tuple[ResultCode, str]:
            """Wrapper method"""
            class_instance = args[0]
            class_instance.logger.debug(
                f"Executing the decorator with: {args}, {kwargs}"
            )

            argin = extract_argin(args)
            task_callback = kwargs["task_callback"]
            task_abort_event = kwargs["task_abort_event"]

            task_callback(status=TaskStatus.IN_PROGRESS)
            setup_data(class_instance)

            if argin:
                result, message = fn(class_instance, argin)
            else:
                result, message = fn(class_instance)

            process_result_and_start_tracker(
                class_instance,
                result,
                message,
                expected_states,
                task_abort_event,
                is_timeout_considered,
                cleanup_function,
            )
            return result, message

        return wrapper

    return error_propagation


def setup_data(class_instance) -> None:
    """Sets up the data required for error propagation."""
    class_name = class_instance.__class__.__name__
    class_instance.component_manager.command_in_progress = class_name
    class_instance.set_command_id(class_name)


def extract_argin(arguments: tuple) -> str:
    """Extracts and returns the argin from the given list of args."""
    for element in arguments:
        if isinstance(element, str):
            return element

    return ""
