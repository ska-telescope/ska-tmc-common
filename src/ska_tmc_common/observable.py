"""
This Module is used to introduce observable class which
maintains list of observers for command completion tracking
"""

from __future__ import annotations

import logging
import threading
from copy import copy
from typing import TYPE_CHECKING

from ska_ser_logging import configure_logging

if TYPE_CHECKING:
    from ska_tmc_common.observer import Observer

configure_logging()
logger = logging.getLogger("observable")


class Observable:
    """The class maintains the list of observers
    and informs them about the notification.
    """

    def __init__(self):
        """Initialization"""
        self.lock = threading.RLock()
        self.observers: list = []

    def register_observer(self, observer: Observer) -> None:
        """This method registers the observers.

        Args:
            observer (Observer): Observer class instance.
        """
        with self.lock:
            logger.info("registered : %s ", observer)
            self.observers.append(observer)

    def deregister_observer(self, observer: Observer) -> None:
        """This method deregister observers

        Args:
            observer (Observer): observer class instance.
        """
        try:
            logger.info("Deregistering observer")
            logger.info("%s", self.observers)
            with self.lock:
                self.observers.remove(observer)
                logger.info("deregistered : %s ", observer)
        except Exception as e:
            logger.error("The exception is: %s", e)

    def notify_observers(
        self,
        *args: list,
        **kwargs: dict,
    ) -> None:
        """This method notifies all observers regarding the event received.

        Args:
            command_exception (bool, optional):
            Denotes whether command exception event. Defaults to False.
            attribute_value_change (bool, optional):
            Denotes whether attribute change event. Defaults to False.
        """
        with self.lock:
            current_observers = copy(self.observers)
            for observer in current_observers:
                logger.info(
                    "Calling observer %s",
                    observer.command_callback_tracker.command_id,
                )
                observer.notify(*args, **kwargs)
