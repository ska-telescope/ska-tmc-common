"""A module implementing a decorator for Error Propagation."""
from threading import Event
from typing import Callable, Optional

from ska_tango_base.commands import ResultCode


def process_result_and_start_tracker(
    class_instance,
    result: ResultCode,
    message: str,
    expected_states: list,
    task_abort_event: Event,
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
    :param cleanup_function: Optional function that cleans up the device after
        command failure
    :type cleanup_function: Optional[Callable]

    :rtype: None
    """
    if result == ResultCode.FAILED:
        class_instance.update_task_status(result=result, message=message)
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
    expected_states: list, cleanup_function: Optional[Callable] = None
) -> Callable:
    """A decorator for implementing error propagation functionality using
    expected states as an input data.

    :param expected_states: The list of states that the device is expected to
        achieve during the course of the command.
    :type expected_states: List
    :param cleanup_function: Optional function that cleans up the device after
        command failure
    :type cleanup_function: Optional[Callable]

    :rtype: Callable function
    """

    def error_propagation(fn: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> tuple[ResultCode, str]:
            """Wrapper method"""
            class_instance = args[0]
            class_name = class_instance.__class__.__name__
            task_abort_event = kwargs["task_abort_event"]
            class_instance.component_manager.command_in_progress = class_name
            class_instance.set_command_id(class_name)
            result, message = fn(*args, **kwargs)
            process_result_and_start_tracker(
                class_instance,
                result,
                message,
                expected_states,
                task_abort_event,
                cleanup_function,
            )
            return result, message

        return wrapper

    return error_propagation
