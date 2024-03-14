"""A module implementing a decorator for Error Propagation."""
import logging
from operator import methodcaller
from threading import Event
from typing import Callable

from ska_ser_logging.configuration import configure_logging
from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus

configure_logging()
logger = logging.getLogger(__name__)


def process_result_and_start_tracker(
    class_instance,
    result: ResultCode,
    message: str,
    expected_states: list,
    task_abort_event: Event,
    is_timeout_considered: bool,
    cleanup_function: str = "",
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
    :type cleanup_function: str

    :rtype: None
    """
    if result == ResultCode.FAILED:
        class_instance.update_task_status(result=result, message=message)
        if is_timeout_considered:
            class_instance.timekeeper.stop_timer()
        if cleanup_function:
            function = methodcaller(cleanup_function)
            function(class_instance)
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
    cleanup_function: str = "",
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
    :type cleanup_function: str

    :rtype: Callable
    """

    def error_propagation(function: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> None:
            """Wrapper method"""
            logger.debug(
                "Executing the error propagation decorator with: %s, %s",
                args,
                kwargs,
            )
            class_instance = args[0]

            argin = extract_argin(args)
            class_instance.task_callback = kwargs["task_callback"]
            task_abort_event = kwargs["task_abort_event"]

            class_instance.task_callback(status=TaskStatus.IN_PROGRESS)
            setup_data(class_instance)

            if argin:
                result, message = function(class_instance, argin)
            else:
                result, message = function(class_instance)

            process_result_and_start_tracker(
                class_instance,
                result,
                message,
                expected_states,
                task_abort_event,
                is_timeout_considered,
                cleanup_function,
            )

        return wrapper

    return error_propagation


def setup_data(class_instance) -> None:
    """Sets up the data required for error propagation.

    :param class_instance: Instance of command class

    :rtype: None
    """
    class_name = class_instance.__class__.__name__
    class_instance.component_manager.command_in_progress = class_name
    class_instance.set_command_id(class_name)


def extract_argin(arguments: tuple) -> str:
    """Extracts and returns the argin from the given list of args.

    :param arguments: The input arguments to the function
    :type arguments: Tuple

    :rtype: str
    """
    for element in arguments:
        if isinstance(element, str):
            return element

    return ""
