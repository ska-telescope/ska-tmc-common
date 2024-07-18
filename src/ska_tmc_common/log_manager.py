""" Class for managing logs."""
from __future__ import annotations

import time


class LogManager:
    """Class for managing logs."""

    def __init__(self: LogManager, max_waiting_time: int = 5):
        self.log_type_to_last_logged_time: dict[str, float] = {}
        self.max_waiting_time: int = max_waiting_time

    def last_log_type_time(self: LogManager, log_type: str) -> float | None:
        """This method will return the time when the log of the
          specified log type was last executed.

        :param log_type : The type of log.
        :type log_type : str

        :return: The times when the log of the specified type was last
                executed.
        :rtype: float | None
        """
        last_logged_time = self.log_type_to_last_logged_time.get(
            log_type, None
        )
        return last_logged_time

    def is_loging_allowed(self, log_type: str) -> bool:
        """checks if log of log_type is allowed i.e waited sufficient before
        repititive logging

        :param log_type : The type of log.
        :type log_type : str

        :return: returns True if log is allowed
        :rtype: bool"""

        current_time = time.time()
        last_logged_time = self.last_log_type_time(log_type)

        if last_logged_time is None:
            self.log_type_to_last_logged_time[log_type] = current_time
            return True

        if current_time - last_logged_time >= self.max_waiting_time:
            self.log_type_to_last_logged_time[log_type] = current_time
            return True

        return False
