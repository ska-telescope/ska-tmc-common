"""
This Module utilized to initialize observers for command completion.
"""

from __future__ import annotations

import logging
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ska_tmc_common.command_callback_tracker import CommandCallbackTracker
    from ska_tmc_common.observable import Observable


class Observer:
    """Observer class utilized to monitor \
        and notify command callback tracker
    """

    def __init__(
        self: Observer,
        logger: logging.Logger,
        command_callback_tracker: CommandCallbackTracker,
        observable: Observable,
    ) -> None:
        """Initialization

        Args:
            self (Observer): class instance
            logger (logging.Logger): logger
            command_callback_tracker (CommandCallbackTracker):
            command callback tracker instance
            observable (Observable): observable instance
        """
        observable.register_observer(self)
        self.logger = logger
        self.command_callback_tracker = command_callback_tracker

    @abstractmethod
    def notify(
        self: Observer,
        *args: list,
        **kwargs: dict,
    ) -> None:
        """This method is to update relevant method

        Args:
            self (Observer): observer instance
        """


class LongRunningCommandExceptionObserver(Observer):
    """Observer class utilized to monitor \
        and notify command callback tracker
    """

    def notify(self, *args, **kwargs):
        """Notifies about the update of command exception"""
        if "command_exception" in args or kwargs.get("command_exception"):
            self.command_callback_tracker.update_exception()


class AttributeValueObserver(Observer):
    """Observer class utilized to monitor \
        and notify command callback tracker
    """

    def notify(self, *args, **kwargs):
        """
        Notifies about the update of attribute state
        """
        if "attribute_value_change" in args or kwargs.get(
            "attribute_value_change"
        ):
            self.command_callback_tracker.update_attr_value_change()
