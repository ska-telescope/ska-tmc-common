"""
This Module utilized to initialize observers for command completion.
"""

from __future__ import annotations

import logging
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

    def notify(
        self: Observer,
        command_exception: bool = False,
        attribute_value_change: bool = False,
    ) -> None:
        """This method notifies command callback tracker about
        the event received.

        Args:
            command_exception (bool, optional):
            Denotes whether command exception event. Defaults to False.
            attribute_value_change (bool, optional):
            Denotes whether attribute change event. Defaults to False.
        """
        if command_exception:
            self.command_callback_tracker.update_exception()
        elif attribute_value_change:
            self.command_callback_tracker.update_attr_value_change()
