"""This module utilized to handle command completion tracker.
"""

from __future__ import annotations

import logging
import threading
from operator import methodcaller
from typing import TYPE_CHECKING

from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus

from ska_tmc_common.observer import (
    AttributeValueObserver,
    LongRunningCommandExceptionObserver,
)

if TYPE_CHECKING:
    from ska_tmc_common.tmc_command import BaseTMCCommand


class CommandCallbackTracker:
    """CommandCallbackTracker class helps to track command status
    with help of multiple callbacks.
    """

    def __init__(
        self,
        command_class_instance: BaseTMCCommand,
        logger: logging.Logger,
        abort_event: threading.Event,
        get_function: str,
        states_to_track: list,
    ):
        """Initialization

        Args:
            command_class_instance (_type_): Command class instance.
            logger (logging.Logger): logger.
            abort_event (BaseTMCCommand): abort event.
            get_function (str): function to check recent event.
            states_to_track (list): states to track.
        """
        self.states_to_track = states_to_track.copy()
        self.logger = logger
        self.abort_event = abort_event
        self.command_class_instance = command_class_instance
        self.component_manager = command_class_instance.component_manager
        self.command_completed: bool = False
        self.command_id = self.component_manager.command_id
        self.get_function = methodcaller(get_function)
        self.lrcr_callback = (
            self.component_manager.long_running_result_callback
        )
        self.observable = self.component_manager.observable
        self.lrc_exception_observer = LongRunningCommandExceptionObserver(
            logger, self, self.observable
        )
        self.attribute_change_observer = AttributeValueObserver(
            logger, self, self.observable
        )
        self.update_attr_value_change()

    def update_timeout_occurred(self):
        """This method is called when timeout occurs."""
        if not self.command_completed:
            self.command_class_instance.update_task_status(
                result=(
                    ResultCode.FAILED,
                    "Timeout has occurred, command failed",
                ),
                exception="Timeout has occurred, command failed",
            )
            self.clean_up()

    def update_attr_value_change(self):
        """This method is invoked when attribute changes."""
        try:
            attribute_value = self.get_function(self.component_manager)
            if not self.command_completed and not self.abort_event.is_set():
                if attribute_value == self.states_to_track[0]:
                    self.states_to_track.remove(attribute_value)
                else:
                    self.logger.debug(
                        "attribute values waiting for: %s "
                        + "and received: %s",
                        self.states_to_track,
                        attribute_value,
                    )
                if not self.states_to_track:  # the list is empty
                    self.command_class_instance.update_task_status(
                        result=(ResultCode.OK, "Command Completed")
                    )
                    self.clean_up()
            elif self.abort_event.is_set():
                self.clean_up()
                self.command_class_instance.update_task_status(
                    status=TaskStatus.ABORTED
                )
        except (AttributeError, ValueError, TypeError) as exception:
            self.logger.error(
                "Error occurred while attribute" + "update %s", exception
            )

    def update_exception(self):
        """This method is invoked when exception occurs."""
        try:
            if not self.command_completed and not self.abort_event.is_set():
                self.command_class_instance.update_task_status(
                    result=(
                        ResultCode.FAILED,
                        self.lrcr_callback.command_data[self.command_id][
                            "exception_message"
                        ],
                    ),
                    exception=self.lrcr_callback.command_data[self.command_id][
                        "exception_message"
                    ],
                )
                self.clean_up()
        except (AttributeError, ValueError, TypeError) as exception:
            self.logger.error(
                "Error occurred while updating exception %s", exception
            )

    def clean_up(self):
        """
        This method is used for clean up of command variables and
        stopping timer.
        """
        try:
            if hasattr(self.command_class_instance, "timekeeper"):
                self.command_class_instance.timekeeper.stop_timer()
            else:
                self.component_manager.stop_timer()
            self.abort_event.clear()
            self.command_completed = True
            self.observable.deregister_observer(self.lrc_exception_observer)
            self.observable.deregister_observer(self.attribute_change_observer)
            if self.component_manager.command_id:
                self.lrcr_callback.remove_data(self.command_id)
        except (AttributeError, ValueError, TypeError) as exception:
            self.logger.error("Error occurred while clean up %s", exception)