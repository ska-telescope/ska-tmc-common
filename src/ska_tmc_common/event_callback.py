"""Event callback class"""

# pylint: disable=broad-exception-caught
import logging
from typing import Any

import tango
from ska_ser_logging.configuration import configure_logging

configure_logging()
LOGGER = logging.getLogger(__name__)


class EventCallback:
    """Simple event callback class."""

    def __init__(self, event_callback: Any) -> None:
        self.events = []
        self.event_callback = event_callback

    def get_events(self):
        """Returns the list of events received by this callback

        :return: the list of events received by this callback
        :rtype: sequence<obj>
        """
        return self.events

    def push_event(self, event_data: tango.EventData):
        """Push event method to utilize this class as a callback."""
        self.events.append(event_data)
        try:
            if not self.check_event_error(event_data=event_data):
                self.event_callback(event_data)
        except Exception as exception:
            LOGGER.exception(
                "Unexpected exception " + "in pushing the event %s : %s",
                event_data.attr_value.name,
                exception,
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
