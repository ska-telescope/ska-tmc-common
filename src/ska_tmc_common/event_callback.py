"""Event callback class"""
# pylint: disable=broad-exception-caught
import logging
from datetime import datetime
from typing import List

import tango
from ska_ser_logging.configuration import configure_logging

from ska_tmc_common.test_helpers.helper_cm_and_event_receiver import (
    SimpleComponentManager,
)

configure_logging()
LOGGER = logging.getLogger(__name__)


class EventCallback:
    """Simple event callback class."""

    def __init__(
        self, callback_name: str, component_manager: SimpleComponentManager
    ) -> None:
        self.callback_name: str = callback_name
        self.events = []
        self.component_manager = component_manager
        self._event_enter_exit_time: List[datetime] = []

    def get_events(self):
        """Returns the list of events received by this callback

        :return: the list of events received by this callback
        :rtype: sequence<obj>
        """
        return self.events

    def push_event(self, event_data: tango.EventData):
        """Push event method to use this class as a callback."""
        self.events.append(event_data)
        try:
            self.log_event_data(event_data, self.callback_name)
            if not self.check_event_error(event_data):
                self.component_manager.process_event(
                    event_data.device.dev_name(),
                    event_data.attr_value.name,
                    event_data.attr_value.value,
                )
            self.log_event_exit(self.callback_name)
        except Exception as exception:
            LOGGER.exception(
                "Unexpected exception in calling the callback: %s", exception
            )

    def log_event_data(
        self, event_data: tango.EventData, callback_name: str
    ) -> None:
        """Log the event data for later use."""
        if event_data.attr_value:
            attribute_name = event_data.attr_value.name
            attribute_value = event_data.attr_value.value
            reception_time: datetime = event_data.attr_value.time.todatetime()
            current_time = datetime.utcnow()
            self._event_enter_exit_time.append(current_time)
            current_time = current_time.strftime("%d/%m/%Y %H:%M:%S:%f")
            LOGGER.info(
                "Enter time for the callback: %s is %s. Event data is - "
                + "Attribute: %s, Value: %s, Reception time: %s",
                callback_name,
                current_time,
                attribute_name,
                attribute_value,
                reception_time.strftime("%d/%m/%Y %H:%M:%S:%f"),
            )

    def log_event_exit(self, callback_name: str) -> None:
        """Log the time of exiting the event."""
        self._event_enter_exit_time.append(datetime.utcnow())
        if len(self._event_enter_exit_time) == 2:
            time_diff = (
                self._event_enter_exit_time[1] - self._event_enter_exit_time[0]
            ).total_seconds()
        else:
            time_diff = datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S:%f")
        self._event_enter_exit_time.clear()
        LOGGER.info(
            "Exit time for the callback: %s is %s", callback_name, time_diff
        )

    def check_event_error(self, event_data: tango.EventData) -> bool:
        """Method for checking event error."""
        if event_data.err:
            error = event_data.errors[0]
            LOGGER.error(
                "Error occured in an event: %s, %s", error.reason, error.desc
            )
            return True
        return False
