"""A module that implements the timekeeper class"""
import threading
from logging import Logger

from ska_tmc_common.enum import TimeoutState
from ska_tmc_common.timeout_callback import TimeoutCallback


class TimeKeeper:
    """A class that maintains the functions required for the timeout
    functionality.
    """

    def __init__(self, time_out: int, logger: Logger) -> None:
        self.time_out = time_out
        self.logger = logger
        self.timer_object: threading.Timer

    def start_timer(
        self, timeout_id: str, timeout_callback: TimeoutCallback
    ) -> None:
        """Starts a timer for the command execution which will run for the
        specified amount of time. After the timer runs out, it will execute the
        timeout handler method.

        :param timeout_id: Id for TimeoutCallback class object.
        :type timeout_id: str

        :param timeout_callback: An instance of TimeoutCallback class that acts
                    as a callable functions to call in the event of timeout.
        :type timeout_callback: TimeoutCallback

        :rtype: None
        """
        try:
            self.timer_object = threading.Timer(
                interval=self.time_out,
                function=self.timeout_handler,
                args=[timeout_id, timeout_callback],
            )
            self.logger.info(f"Starting timer for id : {timeout_id}")
            self.timer_object.start()
        except Exception as exp_msg:
            self.logger.info(f"Issue for  id : {timeout_id}")
            self.logger.exception(
                "Exception occured while starting the timer thread : %s",
                exp_msg,
            )

    def timeout_handler(
        self, timeout_id: str, timeout_callback: TimeoutCallback
    ) -> None:
        """Updates the timeout callback to reflect timeout failure.

        :param timeout_id: Id for TimeoutCallback class object.
        :type timeout_id: str

        :param timeout_callback: An instance of TimeoutCallback class that acts
                    as a callable functions to call in the event of timeout.
        :type timeout_callback: TimeoutCallback

        :rtype: None
        """
        self.logger.info(f"Timeout occured for id : {timeout_id}")
        timeout_callback(
            timeout_id=timeout_id, timeout_state=TimeoutState.OCCURED
        )

    def stop_timer(self) -> None:
        """Stops the timer for command execution"""
        self.logger.info("Stopping timer %s", self.timer_object)
        self.timer_object.cancel()
