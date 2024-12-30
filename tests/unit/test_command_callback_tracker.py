import logging
import threading
from unittest.mock import Mock

from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus

from ska_tmc_common.command_callback_tracker import CommandCallbackTracker


def test_command_callback_tracker_update_timeout_occurred():
    command_class_instance = Mock()
    cct = CommandCallbackTracker(
        command_class_instance, logging, threading.Event(), "get_state", ["ON"]
    )
    cct.update_timeout_occurred()
    command_class_instance.update_task_status.assert_called_with(
        result=(
            ResultCode.FAILED,
            "Timeout has occurred, command failed",
        ),
        exception="Timeout has occurred, command failed",
    )
    cct.update_timeout_occurred()
    assert command_class_instance.update_task_status.call_count == 1


def test_command_callback_tracker_attr_change():
    attrs = {"component_manager.get_state.return_value": "ON"}
    abort_event = threading.Event()
    command_class_instance = Mock(**attrs)
    cct = CommandCallbackTracker(
        command_class_instance, logging, abort_event, "get_state", ["ON"]
    )
    cct.update_attr_value_change()
    command_class_instance.update_task_status.assert_called_with(
        result=(ResultCode.OK, "Command Completed")
    )
    cct.update_attr_value_change()
    assert command_class_instance.update_task_status.call_count == 1


def test_abort_command_callback_tracker_attr_change():
    attrs = {"component_manager.get_state.return_value": "ON"}
    abort_event = threading.Event()
    command_class_instance = Mock(**attrs)
    cct = CommandCallbackTracker(
        command_class_instance, logging, abort_event, "get_state", ["ON"]
    )
    abort_event.set()
    cct.update_attr_value_change()
    command_class_instance.update_task_status.assert_called_with(
        status=TaskStatus.ABORTED
    )


def test_command_callback_tracker_command_exp():
    command_class_instance = Mock()
    cct = CommandCallbackTracker(
        command_class_instance, logging, threading.Event(), "get_state", ["ON"]
    )
    cct.command_id = 1
    cct.lrcr_callback.command_data = {
        1: {"exception_message": "Exception message"}
    }
    cct.update_exception()
    command_class_instance.update_task_status.assert_called_with(
        result=(ResultCode.FAILED, "Exception message"),
        exception="Exception message",
    )
    cct.update_exception()
    assert command_class_instance.update_task_status.call_count == 1


def test_abort_command_callback_tracker_command_exp():
    command_class_instance = Mock()
    abort_event = threading.Event()
    cct = CommandCallbackTracker(
        command_class_instance, logging, abort_event, "get_state", ["ON"]
    )
    abort_event.set()
    cct.command_id = 1
    cct.lrcr_callback.command_data = {
        1: {"exception_message": "Exception message"}
    }
    cct.update_exception()
    command_class_instance.update_task_status.assert_not_called()


def test_clean_up():
    attrs = {"timekeeper.stop_timer.return_value": True}
    command_class_instance = Mock(**attrs)
    abort_event = threading.Event()
    cct = CommandCallbackTracker(
        command_class_instance, logging, abort_event, "get_state", ["ON"]
    )
    abort_event.set()
    cct.clean_up()
    command_class_instance.timekeeper.stop_timer.assert_called_once()
